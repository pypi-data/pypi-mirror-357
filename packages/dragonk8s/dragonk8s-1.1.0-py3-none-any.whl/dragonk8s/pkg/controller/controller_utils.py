import copy
import threading

import time

import logging

from kubernetes.client.models.v1_pod_template_spec import V1PodTemplateSpec
from kubernetes.client.models.v1_owner_reference import V1OwnerReference
from dragonk8s.lib.client.tools import cache
from kubernetes import client
from dragonk8s.lib.client.tools import events
from kubernetes.client.models import V1ObjectMeta
from kubernetes.client.models import V1Pod
from kubernetes.client import models as kube_models
from kubernetes.client.exceptions import ApiException
from dragonk8s.lib.apimachinery.pkg.api import errors
from dragonk8s.lib.apimachinery.pkg.types.patch import *
from dragonk8s.lib.apimeta import apigvk
from dragonk8s.lib.models import corev1
from dragonk8s.lib.apimachinery.pkg.apis import meta_v1
from dragonk8s.lib.apimachinery.pkg import labels


ExpectationsTimeout = 5 * 60
FailedCreatePodReason = "FailedCreate"
SuccessfulCreatePodReason = "SuccessfulCreate"
FailedDeletePodReason = "FailedDelete"
SuccessfulDeletePodReason = "SuccessfulDelete"


class PodControlInterface(object):

    def create_pod(self, namespace: str, template: V1PodTemplateSpec, obj, controller_ref: V1OwnerReference):
        pass

    def create_pod_with_generate_name(self, namespace: str, template: V1PodTemplateSpec, obj,
                                      controller_ref: V1OwnerReference, generate_name: str):
        pass

    def delete_pod(self, namespace: str, pod_id: str, obj):
        pass

    def patch_pod(self, namespace: str, name: str, data: dict):
        pass


class ControlleeExpectations(object):

    def __init__(self, add: int, dele: int, key: str, timestamp: float):
        self.addn = add
        self.deln = dele
        self.key = key
        self.timestamp = timestamp

    def add(self, addn: int, deln: int):
        self.addn += addn
        self.deln = deln

    def fulfilled(self) -> bool:
        return self.addn <= 0 and self.deln <= 0

    def get_expectations(self) -> (int, int):
        return self.addn, self.deln

    def is_expired(self):
        return time.time() - self.timestamp > ExpectationsTimeout

    def __repr__(self):
        return "(key=%s, add=%d, del=%d, timestamp=%d)" % (self.key, self.addn, self.deln, self.timestamp)

    def __str__(self):
        return self.__repr__()


class ControllerExpectationsInterface(object):

    def get_expectations(self, controllerkey: str) -> (ControlleeExpectations, bool):
        pass

    def satisfied_expectations(self, controllerkey: str) -> bool:
        pass

    def delete_expectations(self, controllerkey: str):
        pass

    def set_expectations(self, controllerkey: str, addn: int, deln: int):
        pass

    def expect_creations(self, controllerkey: str, addns: int):
        pass

    def expect_deletions(self, controllerkey: str, delns: int):
        pass

    def creation_observed(self, controllerkey: str):
        pass

    def deletion_observed(self, controllerkey: str):
        pass

    def raise_expectations(self, controllerkey: str, addn: int, deln: int):
        pass

    def lower_expectations(self, controllerkey: str, addn: int, deln: int):
        pass


def exp_key_func(obj) -> str:
    return obj.key


class ControllerExpectations(ControllerExpectationsInterface):
    def __init__(self):
        super().__init__()
        self.cache = cache.Cache(key_func=exp_key_func, indexers={})

    def get_expectations(self, controllerkey: str) -> (ControlleeExpectations, bool):
        exp, exists = self.cache.get_by_key(controllerkey)
        if exists:
            return exp, True
        return None, False

    def satisfied_expectations(self, controllerkey: str) -> bool:
        exp, exists = self.cache.get_by_key(controllerkey)
        if not exists:
            logging.info("Controller %s either never recorded expectations, or the ttl expired" % controllerkey)
        else:
            if exp.fulfilled():
                logging.info("Controller expectations fulfilled: %s" % exp)
                return True
            elif exp.is_expired():
                logging.info("Controller expectations expired %s" % exp)
                return True
            else:
                logging.info("Controller still waiting on expectations %s" % exp)
                return False
        return True

    def delete_expectations(self, controllerkey: str):
        exp, exists = self.cache.get_by_key(controllerkey)
        if exists:
            self.cache.delete(exp)

    def set_expectations(self, controllerkey: str, addn: int, deln: int):
        exp = ControlleeExpectations(add=addn, dele=deln, key=controllerkey, timestamp=time.time())
        logging.info("Setting expectations %s" % exp)
        return self.cache.add(exp)

    def expect_creations(self, controllerkey: str, addns: int):
        return self.set_expectations(controllerkey, addns, 0)

    def expect_deletions(self, controllerkey: str, delns: int):
        return self.set_expectations(controllerkey, 0, delns)

    def creation_observed(self, controllerkey: str):
        self.lower_expectations(controllerkey, 1, 0)

    def deletion_observed(self, controllerkey: str):
        self.lower_expectations(controllerkey, 0, 1)

    def raise_expectations(self, controllerkey: str, addn: int, deln: int):
        exp, exists = self.get_expectations(controllerkey)
        if exists:
            exp.add(addn, deln)
            logging.info("raise expectations %s" % exp)

    def lower_expectations(self, controllerkey: str, addn: int, deln: int):
        exp, exists = self.get_expectations(controllerkey)
        if exists:
            exp.add(-1 * addn, -1 * deln)
            logging.info("lowered expectations %s" % exp)


def _validate_controller_ref(controller_ref: V1OwnerReference):
    if controller_ref is None:
        raise Exception("controllerRef is None")
    if len(controller_ref.api_version) == 0:
        raise Exception("controllerRef has empty api version")
    if len(controller_ref.kind) == 0:
        raise Exception("controllerRef has empty kind")
    if not controller_ref.controller:
        raise Exception("controllerRef.Controller is not set to true")
    if not controller_ref.block_owner_deletion:
        raise Exception("controllerRef.BlockOwnerDeletin is not set")


def _get_pods_label_set(template: V1PodTemplateSpec) -> dict:
    desired_labels = dict()
    if not template.metadata.labels:
        return desired_labels
    for k, v in template.metadata.labels.items():
        desired_labels[k] = v
    return desired_labels


def _get_pods_finalizers(template: V1PodTemplateSpec) -> list:
    desired_finalizers = copy.copy(template.metadata.finalizers)
    return desired_finalizers


def _get_pods_annotation_set(template: V1PodTemplateSpec) -> dict:
    desired_annotations = dict()
    if not template.metadata.annotations:
        return desired_annotations
    for k, v in template.metadata.annotations.items():
        desired_annotations[k] = v
    return desired_annotations


def get_pod_from_template(template: V1PodTemplateSpec, parent_object, controller_ref: V1OwnerReference) -> V1Pod:
    desired_labels = _get_pods_label_set(template)
    desired_finalizers = _get_pods_finalizers(template)
    desired_annotations = _get_pods_annotation_set(template)
    prefix = _get_pods_prefix(parent_object.metadata.name)
    pod = V1Pod(
        metadata=V1ObjectMeta(
            labels=desired_labels,
            annotations=desired_annotations,
            generate_name=prefix,
            finalizers=desired_finalizers,
        )
    )
    if controller_ref is not None:
        pod.metadata.owner_references = [copy.deepcopy(controller_ref)]
    pod.spec = copy.deepcopy(template.spec)
    return pod


def _get_pods_prefix(controller_name: str) -> str:
    prefix = "%s-" % controller_name
    # todo: validate
    return prefix


class RealPodControl(PodControlInterface):

    def __init__(self, kube_client, recorder: events.EventRecorder):
        self.kube_client = apigvk.get_resource_client(kube_client, apigvk.CoreV1Pod)
        self.recorder = recorder

    def _create_pod(self, namespace: str, pod: V1Pod, obj):
        if not pod.metadata.labels:
            raise Exception("unable to create pods , no labels")
        pod.metadata.namespace = namespace
        try:
            new_pod = self.kube_client.create(pod)
        except ApiException as e:
            if errors.has_status_cause(e, errors.NamespaceTerminatingCause):
                self.recorder.eventf(obj, None, events.EventTypeWarning, FailedCreatePodReason,
                                     "CreatePod", "Error creating: %s", str(e))
            raise e
        logging.info("Controller %s created pod %s", obj.metadata.name, new_pod.metadata.name)
        self.recorder.eventf(obj, None, events.EventTypeNormal, SuccessfulCreatePodReason,
                             SuccessfulCreatePodReason, "created pod: %s" % new_pod.metadata.name)

    def create_pod(self, namespace: str, template: V1PodTemplateSpec, obj, controller_ref: V1OwnerReference):
        self.create_pod_with_generate_name(namespace, template, obj, controller_ref, "")

    def create_pod_with_generate_name(self, namespace: str, template: V1PodTemplateSpec, obj,
                                      controller_ref: V1OwnerReference, generate_name: str):
        _validate_controller_ref(controller_ref)
        pod = get_pod_from_template(template, obj, controller_ref)
        if generate_name:
            pod.metadata.generate_name = generate_name
        return self._create_pod(namespace, pod, obj)

    def delete_pod(self, namespace: str, pod_id: str, obj):
        logging.info("deleting pod(%s) by controller %s" % (pod_id, obj.metadata.name))
        try:
            self.kube_client.delete(name=pod_id, namespace=namespace)
        except ApiException as e:
            if errors.is_not_found(e):
                logging.info("pod %s/%s has already been deleted" % (namespace, pod_id))
                raise e
            self.recorder.eventf(obj, None, events.EventTypeWarning,
                                 FailedDeletePodReason, FailedDeletePodReason, "Error deleting: %s" % str(e))
            raise Exception("unable to delete pods: %s" % str(e))
        except Exception as e:
            self.recorder.eventf(obj, None, events.EventTypeWarning,
                                 FailedDeletePodReason, FailedDeletePodReason, "Error deleting: %s" % str(e))
            raise Exception("unable to delete pods: %s" % str(e))
        self.recorder.eventf(obj, None, events.EventTypeNormal,
                             SuccessfulDeletePodReason, SuccessfulDeletePodReason, "Deleted pod: %s" % pod_id)

    def patch_pod(self, namespace: str, name: str, data: dict):
        self.kube_client.patch(body=data, name=name, namespace=namespace, content_type=PatchType.StrategicMergePatchType)


class UIDSet(object):
    def __init__(self, data, key):
        self.data = data
        self.key = key


def uid_set_key_func(obj: UIDSet) -> str:
    return obj.key


class UIDTrackingControllerExpectations(object):

    def __init__(self, ce: ControllerExpectationsInterface):
        self.ce = ce
        self.lock = threading.Lock()
        self.uid_store = cache.Cache(key_func=uid_set_key_func, indexers={})

    def get_uids(self, controller_key: str) -> list:
        uid, exists = self.uid_store.get_by_key(controller_key)
        if exists:
            return uid.data
        return []

    def expect_deletions(self, rc_key, deleted_keys):
        expected_uids = list(set(deleted_keys))
        existing = self.get_uids(rc_key)
        if len(existing) > 0:
            logging.error("Clobbering existing delete keys: %s" % str(existing))
        self.uid_store.add(UIDSet(data=expected_uids, key=rc_key))
        self.ce.expect_deletions(rc_key, len(expected_uids))

    def deletion_observed(self, rc_key, delete_key):
        try:
            self.lock.acquire()
            uids = self.get_uids(rc_key)
            print("uids: %s" % str(uids))
            if delete_key in uids:
                logging.info("Controller %s received delete for pod %s" % (rc_key, delete_key))
                self.ce.deletion_observed(rc_key)
                uids.remove(delete_key)
        finally:
            self.lock.release()

    def delete_expectations(self, rc_key):
        try:
            self.lock.acquire()
            self.ce.delete_expectations(rc_key)
            uid_exp, exists = self.uid_store.get_by_key(rc_key)
            if exists:
                self.uid_store.delete(uid_exp)

        finally:
            self.lock.release()


class RSControlInterface(object):

    def patch_replica_set(self, namespace: str, name: str, data: dict):
        pass


class RealRSControl(RSControlInterface):

    def __init__(self, client, recorder):
        self.kube_client = client
        self.recorder = recorder

    def patch_replica_set(self, namespace: str, name: str, data: dict):
        self.kube_client.patch(body=data, name=name, namespace=namespace, content_type=PatchType.MergePatchType)


class ControllerRevisionControlInterface(object):

    def patch_controller_revision(self, namespace: str, name: str, data: dict):
        pass


class RealControllerRevisionControl(ControllerRevisionControlInterface):

    def __init__(self, kube_client):
        self.kube_client = kube_client

    def patch_controller_revision(self, namespace: str, name: str, data: dict):
        apigvk.get_resource_client(self.kube_client, apigvk.AppsV1ControllerRevision).patch(
            body=data, name=name, namespace=namespace, content_type=PatchType.StrategicMergePatchType)


def is_pod_active(p: V1Pod) -> bool:
    return p.status.phase not in (corev1.PodStatus.PodSucceeded, corev1.PodStatus.PodFailed) and \
           p.metadata.deletion_timestamp is None


def filter_active_pods(pods: list) -> list:
    res = []
    for p in pods:
        if is_pod_active(p):
            res.append(p)
        else:
            logging.info("Ignoring inactive pod %s/%s in state %s, deletion time: %s"
                         % (p.metadata.namespace, p.metadata.name, p.status.phase, p.metadata.deletion_timestamp))
    return res


def recheck_deletion_timestamp(get_object):
    def do():
        try:
            obj = get_object()
        except Exception as e:
            raise Exception("can't recheck deletion_timestamp: %s" % str(e))
        if obj.metadata.deletion_timestamp is not None:
            raise Exception("%s/%s has just been deleted at: %s"
                            % (obj.metadata.namespace, obj.metadata.name, obj.metadata.deletion_timestamp))
        return
    return do


class BaseControllerRefManager(object):

    def __init__(self, controller, selector, can_adopt_func, lock: threading.Lock):
        self.controller = controller
        self.selector = selector
        self.can_adopt_exception = None
        self.can_adopt_func = can_adopt_func
        self.lock = lock

    def can_adopt(self):
        with self.lock:
            if self.can_adopt_func:
                try:
                    self.can_adopt_func()
                except Exception as e:
                    self.can_adopt_exception = e
                    raise self.can_adopt_exception

    def claim_object(self, obj, match, adopt, release) -> bool:
        controller_ref = meta_v1.get_controller_of_no_copy(obj)
        if controller_ref:
            if controller_ref.uid != self.controller.metadata.uid:
                return False
            if match(obj):
                return True
            if self.controller.metadata.deletion_timestamp:
                return False
            try:
                release(obj)
            except errors.ApiException as e:
                if errors.is_not_found(e):
                    return False
            return False
        if self.controller.metadata.deletion_timestamp or not match(obj):
            return False
        if obj.metadata.deletion_timestamp:
            return False
        if len(self.controller.metadata.namespace) > 0 and self.controller.metadata.namespace != obj.metadata.namespace:
            return False
        try:
            adopt(obj)
        except errors.ApiException as e:
            if errors.is_not_found(e):
                return False
        return True


def _owner_ref_controller_patch(controller, controller_kind: apigvk.GVK, uid: str, *finalizers) -> dict:
    res = dict(
        metadata=dict(
            uid=uid,
            ownerReferences=[
                dict(
                    apiVersion=controller_kind.version,
                    kind=controller_kind.kind,
                    uid=controller.metadata.uid,
                    controller=True,
                    blockOwnerDeletion=True,
                )
            ],
            finalizers=finalizers
        )
    )
    return res


def _owner_reference(uid: str, patch_type) -> dict:
    return {
        "$patch": patch_type,
        "uid": uid,
    }


def generate_delete_owner_ref_strategic_merge_data(dependent_uid: str, owner_uids: list, *finalizers) -> dict:
    owner_references = []
    for owner_uid in owner_uids:
        owner_references.append(_owner_reference(owner_uid, "delete"))
    patch = {
        "metadata": {
            "uid": dependent_uid,
            "ownerReferences": owner_references,
            "$deleteFromPrimitiveList/finalizers": finalizers,
        }
    }
    return patch


class PodControllerRefManager(BaseControllerRefManager):

    def __init__(self, pod_control: PodControlInterface,
                 controller, selector, controller_kind: apigvk.GVK, can_adopt_func, *finalizers):
        super(PodControllerRefManager, self).__init__(controller, selector, threading.Lock(), can_adopt_func)
        self.controller_kind = controller_kind
        self.pod_control = pod_control
        self.finalizers = finalizers

    def adopt_pod(self, pod: V1Pod):
        try:
            self.can_adopt()
        except Exception as e:
            raise Exception("can't adopt pod %s/%s (%s): %s"
                            % (pod.metadata.namespace, pod.metadata.name, pod.metadata.uid, str(e)))
        patch_data = _owner_ref_controller_patch(
            self.controller, self.controller_kind, pod.metadata.uid, *self.finalizers)
        self.pod_control.patch_pod(pod.metadata.namespace, pod.metadata.name, patch_data)

    def release_pod(self, pod: V1Pod):
        logging.info("patching pod %s_%s to remove its controllerRef to %s/%s:%s"
                     % (pod.metadata.namespace, pod.metadata.name, self.controller_kind.group_version,
                        self.controller_kind.kind, self.controller.metadata.name))
        patch_data = generate_delete_owner_ref_strategic_merge_data(
            pod.metadata.uid, [self.controller.metadata.uid], *self.finalizers)
        try:
            self.pod_control.patch_pod(pod.metadata.namespace, pod.metadata.name, patch_data)
        except errors.ApiException as e:
            if errors.is_not_found(e):
                return
            if errors.is_invalid(e):
                return

    def claim_pods(self, pods: list, *filters) -> list:
        claimed = []

        def match(obj) -> bool:
            pod = obj
            if not self.selector.matches(labels.Set(pod.metadata.labels)):
                return False
            for filter in filters:
                if not filter(pod):
                    return False
            return True

        for pod in pods:
            if self.claim_object(pod, match, self.adopt_pod, self.release_pod):
                claimed.append(pod)
        return claimed


def pod_key(pod: V1Pod) -> str:
    return "{}/{}".format(pod.metadata.namespace, pod.metadata.name)
