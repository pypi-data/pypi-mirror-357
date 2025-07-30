from __future__ import annotations

import copy
import json
import logging
import threading
import time

from dragonk8s.lib.client.informers.informer import BaseInformer
from dragonk8s.lib.client.informers.dragon.replicaset import ReplicaSetInformer
from kubernetes.client.models.v1_event_source import V1EventSource
from dragonk8s.lib.client.kubernetes.typed.core.v1.event_expansion import EventSinkImpl
from dragonk8s.pkg.controller import controller_utils
from dragonk8s.lib.client.util.workqueue import RateLimitingType
from dragonk8s.dragon.models import IoDragonAppsV1ReplicaSet
from kubernetes.client.models import V1Pod, V1OwnerReference
from dragonk8s.lib.apimachinery.pkg.apis import meta_v1
from dragonk8s.lib.client.tools import informer
from dragonk8s.lib.apimachinery.pkg.util import wait
from dragonk8s.lib.apimeta import apigvk
from dragonk8s.lib.client.tools import cache
from dragonk8s.lib.apimachinery.pkg.api import errors
from dragonk8s.lib.apimachinery.pkg import labels
from dragonk8s.pkg.controller.replicaset import replica_set_utils
from dragonk8s.lib.util import timeutil
from dragonk8s.pkg.api.v1 import pod_util
from dragonk8s.lib.pool.thread_manager import GlobalThreadManager
from dragonk8s.lib.client.tools import events


controllerUIDIndex = "controllerUID"


def _get_pod_to_delete(filtered_pods: list, related_pods: list, diff) -> list:
    # todo getPodsRankedByRelatedPodsOnSameNode
    if diff < len(filtered_pods):
        return filtered_pods[:diff]
    logging.warning("diff greater than filtered_pods??")
    return filtered_pods


def _get_pod_keys(pods: list) -> list:
    pod_keys = []
    for pod in pods:
        pod_keys.append(controller_utils.pod_key(pod))
    return pod_keys


class ReplicaSetController(object):

    def __init__(self, rs_informer: ReplicaSetInformer, pod_informer: BaseInformer, kube_client, burst_replicas: int,
                 stop: threading.Event):
        sink = events.EventSinkImpl(kube_client)
        event_broadcaster = events.EventBroadcasterImpl(sink=sink)
        event_broadcaster.start_recording_to_sink(stop)
        event_broadcaster.start_structured_logging(stop)
        # todo: metrics

        self.kube_client = apigvk.get_resource_client(kube_client, apigvk.IoDragonAppsV1ReplicaSet)
        self.pod_control = controller_utils.RealPodControl(
            kube_client=kube_client,
            recorder=event_broadcaster.new_recorder("dragon-replicaset-controller"))
        self.burst_replicas = burst_replicas
        self.expectations = controller_utils.UIDTrackingControllerExpectations(controller_utils.ControllerExpectations())
        self.queue = RateLimitingType()
        self._type = apigvk.IoDragonAppsV1ReplicaSet
        self.stop = stop

        rs_informer.informer().add_event_handler(informer.ResourceEventHandlerFuncs(
            add_func=self._add_rs,
            update_func=self._update_rs,
            delete_func=self._delete_rs,
        ))

        def uid_index(obj) -> list:
            controller_ref = meta_v1.get_controller_of(obj)
            if controller_ref is None:
                return []
            return [controller_ref.uid]
        rs_informer.informer().add_indexers({
            controllerUIDIndex: uid_index,
        })
        self.rs_lister = rs_informer.lister()
        self.rs_indexer = rs_informer.informer().get_indexer()
        self.rs_lister_synced = rs_informer.informer().has_synced

        pod_informer.informer().add_event_handler(informer.ResourceEventHandlerFuncs(
            add_func=self._add_pod,
            update_func=self._update_pod,
            delete_func=self._delete_pod,
        ))
        self.pod_lister = pod_informer.lister()
        self.pod_lister_synced = pod_informer.informer().has_synced
        self.sync_handler = self._sync_replicaset

    def _sync_replicaset(self, key: str):
        logging.info("sync replicaset %s" % key)
        try:
            return self.__sync_replicaset(key)
        finally:
            logging.info("sync replicaset %s done..." % key)

    def _enqueue_rs(self, rs: IoDragonAppsV1ReplicaSet):
        try:
            key = informer.deletion_handling_meta_namespace_key_func(rs)
        except Exception as e:
            logging.error("couldn't get key for %s %s: %s" % (self._type.kind, rs.to_str(), str(e)))
            return
        self.queue.add(key)

    def _enqueue_rs_after(self, rs: IoDragonAppsV1ReplicaSet, duration: int):
        try:
            key = informer.deletion_handling_meta_namespace_key_func(rs)
        except Exception as e:
            logging.error("couldn't get key for %s %s: %s" % (self._type.kind, rs.to_str(), str(e)))
            return
        self.queue.add_after(key, duration)

    def _add_rs(self, obj: IoDragonAppsV1ReplicaSet):
        rs = obj
        logging.info("adding %s %s/%s" % (self._type.kind, rs.metadata.namespace, rs.metadata.name))
        self._enqueue_rs(rs)

    def _update_rs(self, old_obj: IoDragonAppsV1ReplicaSet, new_obj: IoDragonAppsV1ReplicaSet):
        if new_obj.metadata.uid != old_obj.metadata.uid:
            try:
                key = informer.deletion_handling_meta_namespace_key_func(old_obj)
            except Exception as e:
                logging.error("couldn't get key for %s %s: %s" % (self._type.kind, old_obj.to_str(), str(e)))
                return
            self._delete_rs(cache.DeletedFinalStateUnknown(
                key=key,
                obj=old_obj,
            ))
        if old_obj.spec.replicas != new_obj.spec.replicas:
            logging.info("%s %s updated. desired pod count change: %d->%d"
                         % (self._type.kind, new_obj.metadata.name, old_obj.spec.replicas, new_obj.spec.replicas))
        self._enqueue_rs(new_obj)

    def _delete_rs(self, obj: IoDragonAppsV1ReplicaSet|cache.DeletedFinalStateUnknown):
        if not isinstance(obj, IoDragonAppsV1ReplicaSet):
            if not isinstance(obj, cache.DeletedFinalStateUnknown):
                logging.error("couldn't get object from tombstone %s" % (str(obj)))
                return
            rs = obj.obj
        else:
            rs = obj
        try:
            key = informer.deletion_handling_meta_namespace_key_func(rs)
        except Exception as e:
            logging.error("couldn't get key for %s %s: %s" % (self._type.kind, rs.to_str(), str(e)))
            return
        logging.info("Deleting %s %s" % (self._type.kind, key))
        self.expectations.delete_expectations(key)
        self.queue.add(key)

    def _get_pod_replicasets(self, pod: V1Pod) -> list:
        try:
            rss = self.rs_lister.get_pod_replica_sets(pod)
        except Exception as e:
            return []
        if len(rss) > 1:
            logging.error("user error! more than one %s is selecting pods with labels: %s"
                          % (self._type.kind, pod.metadata.labels))
        return rss

    def _add_pod(self, obj: V1Pod):
        pod = obj
        if pod.metadata.deletion_timestamp:
            self._delete_pod(pod)
            return
        controller_ref = meta_v1.get_controller_of(pod)
        if controller_ref:
            rs = self._resolve_controller_ref(pod.metadata.namespace, controller_ref)
            if rs is None:
                return
            try:
                key = informer.deletion_handling_meta_namespace_key_func(rs)
            except Exception as e:
                logging.error("couldn't get key for %s %s: %s" % (self._type.kind, rs.to_str(), str(e)))
                return
            logging.info("Pod %s created: %s" % (pod.metadata.name, pod.metadata.name))
            self.expectations.ce.creation_observed(key)
            self.queue.add(key)
            return
        rss = self._get_pod_replicasets(pod)
        if len(rss) == 0:
            return
        logging.info("Orphan Pod %s created: %s" % (pod.metadata.name, pod.to_str()))
        for rs in rss:
            self._enqueue_rs(rs)

    def _update_pod(self, old_obj: V1Pod, new_obj: V1Pod):
        if old_obj.metadata.resource_version == new_obj.metadata.resource_version:
            return
        label_changed = new_obj.metadata.labels != old_obj.metadata.labels
        if new_obj.metadata.deletion_timestamp:
            self._delete_pod(new_obj)
            if label_changed:
                self._delete_pod(old_obj)
            return
        new_controller_ref = meta_v1.get_controller_of(new_obj)
        old_controller_ref = meta_v1.get_controller_of(old_obj)
        controller_ref_changed = new_controller_ref.to_dict() != old_controller_ref.to_dict()
        if controller_ref_changed and old_controller_ref:
            rs = self._resolve_controller_ref(old_obj.metadata.namespace, old_controller_ref)
            if rs:
                self._enqueue_rs(rs)
        if new_controller_ref:
            rs = self._resolve_controller_ref(new_obj.metadata.namespace, new_controller_ref)
            if rs is None:
                return
            # logging.info("pod %s updated,  %s -> %s" %
            #              (new_obj.metadata.name, old_obj.metadata.to_str(), new_obj.metadata.to_str()))
            logging.info("pod %s updated" % new_obj.metadata.name)
            self._enqueue_rs(rs)
            if not pod_util.is_pod_ready(old_obj) and pod_util.is_pod_ready(new_obj) and rs.spec.min_ready_seconds > 0:
                logging.info("%s %s will be enqueued after %ds for availability check"
                             % (self._type.kind, rs.metadata.name, rs.spec.min_ready_seconds))
                self._enqueue_rs_after(rs, rs.spec.min_ready_seconds+1)
            return
        if label_changed or controller_ref_changed:
            rss = self._get_pod_replicasets(new_obj)
            if len(rss) == 0:
                return
            # logging.info("Orphan Pod %s updated, objectMeta %s -> %s"
            #              % (new_obj.metadata.name, old_obj.metadata.to_str(), new_obj.metadata.to_str()))
            logging.info("Orphan Pod %s updated " % new_obj.metadata.name)
            for rs in rss:
                self._enqueue_rs(rs)

    def _delete_pod(self, obj: V1Pod|cache.DeletedFinalStateUnknown):
        if not isinstance(obj, V1Pod):
            if not isinstance(obj, cache.DeletedFinalStateUnknown):
                logging.error("couldn't get object from tombstone %s" % str(obj))
                return
            pod = obj.obj
        else:
            pod = obj
        controller_ref = meta_v1.get_controller_of(pod)
        if not controller_ref:
            return
        rs = self._resolve_controller_ref(pod.metadata.namespace, controller_ref)
        if not rs:
            return
        try:
            key = informer.deletion_handling_meta_namespace_key_func(rs)
        except Exception as e:
            logging.error("couldn't get key for %s %s: %s" % (self._type.kind, rs.to_str(), str(e)))
            return
        logging.info("pod %s/%s deleted throuth %s, timestamp: %s"
                     % (pod.metadata.name, pod.metadata.name, "dragon-replicaset-controller",
                        timeutil.to_time_str_with_ns(pod.metadata.deletion_timestamp)))
        self.expectations.deletion_observed(key, controller_utils.pod_key(pod))
        self.queue.add(key)

    def _resolve_controller_ref(self, namespace: str, controller_ref: V1OwnerReference) -> IoDragonAppsV1ReplicaSet|None:
        if controller_ref.kind != self._type.kind:
            return None
        try:
            rs = self.rs_lister.with_namespace(namespace).get(controller_ref.name)
        except Exception as e:
            if isinstance(e, errors.ApiException) and errors.is_not_found(e):
                return None
            logging.error("get rs %s error: %s" % (controller_ref.name, str(e)))
            return None
        if rs.metadata.uid != controller_ref.uid:
            return None
        return rs

    def _process_next_work_item(self) -> bool:
        if self.stop.is_set():
            return False
        key, quit = self.queue.get()
        if quit:
            return False
        try:
            self.sync_handler(key)
            # todo
        except Exception as e:
            logging.error("sync %s error: %s" % (key, str(e)))
            self.queue.add_rate_limited(key)
            return True
        else:
            self.queue.forget(key)
            return True
        finally:
            self.queue.done(key)

    def _worker(self):
        while self._process_next_work_item():
            pass
        logging.debug("worker quit")

    def run(self, workers: int):

        def quit():
            while not self.stop.wait():
                continue
            self.queue.shutdown()
        GlobalThreadManager.new_thread(target=quit, generate_name="controller quit").start()
        try:
            controller_name = self._type.kind.lower()
            logging.info("Starting %s controller" % controller_name)
            if not cache.wait_for_named_cache_sync(controller_name, self.stop, self.pod_lister_synced, self.rs_lister_synced):
                return
            for i in range(workers):
                wait.until_with_thread(self._worker, 1, self.stop, "worker-%d" % i)
            logging.info("controller wait to done...")
            self.stop.wait()
            logging.info("Stopping %s controller" % controller_name)
        except Exception as e:
            logging.info("controller run error: %s" % str(e))

    def _get_replicasets_with_same_controller(self, rs: IoDragonAppsV1ReplicaSet) -> list:
        controller_ref = meta_v1.get_controller_of(rs)
        if not controller_ref:
            logging.warning("ReplicaSet has no controller: %s" % rs.to_str())
            return []
        try:
            objs = self.rs_indexer.by_index(controllerUIDIndex, controller_ref.uid)
        except Exception as e:
            logging.error(" index error: %s" % str(e))
            return []
        return objs

    def _get_indirectly_related_pods(self, rs: IoDragonAppsV1ReplicaSet) -> list:
        related_pods = []
        seen = {}
        for related_rs in self._get_replicasets_with_same_controller(rs):
            try:
                selector = meta_v1.labels_selector_as_selector(related_rs.spec.selector)
            except Exception as e:
                logging.error("_get_indirectly_related_pods labels_selector_as_selector error: %s" % str(e))
                continue
            try:
                pods = self.pod_lister.with_namespace(related_rs.metadata.namespace).list(selector)
            except Exception as e:
                logging.error("_get_indirectly_related_pods, list pod error: %s" % str(e))
                return []
            for pod in pods:
                if pod.metadata.uid in seen:
                    other_rs = seen[pod.metadata.uid]
                    logging.info("pod %s/%s is owned by both %s %s/%s and %s %s/%s"
                                 % (pod.metadata.namespace, pod.metadata.name, self._type.kind,
                                    other_rs.metadata.namespace, other_rs.metadata.name, self._type.kind,
                                    related_rs.metadata.namespace, related_rs.metadata.name))
                    continue
                seen[pod.metadata.uid] = related_rs
                related_pods.append(pod)
            logging.info("Found related pods, count %d" % len(related_pods))
            return related_pods

    def _manage_replicas(self, filtered_pods: list, rs: IoDragonAppsV1ReplicaSet):
        logging.info("manage replicas for rs %s/%s" % (rs.metadata.namespace, rs.metadata.name))
        diff = len(filtered_pods) - rs.spec.replicas
        try:
            # cache.DeletionHandlingMetaNamespaceKeyFunc
            rs_key = informer.deletion_handling_meta_namespace_key_func(rs)
        except Exception as e:
            logging.error("couldn't get key for %s %s: %s" % (self._type.kind, rs.metadata.name, str(e)))
            return
        if diff < 0:
            diff = diff * -1
            if diff > self.burst_replicas:
                diff = self.burst_replicas
            self.expectations.ce.expect_creations(rs_key, diff)
            logging.info("Too few replicas, need: %d, creating: %d", rs.spec.replicas, diff)
            # todo: 并行
            success_creations = 0
            for i in range(diff):
                try:
                    self.pod_control.create_pod(
                        rs.metadata.namespace, rs.spec.template, rs, meta_v1.new_controller_ref(rs, self._type))
                except errors.ApiException as e:
                    if errors.has_status_cause(e, errors.NamespaceTerminatingCause):
                        return
                else:
                    success_creations += 1
            skipped_pods = diff - success_creations
            if skipped_pods > 0:
                logging.info("create pods failure, Skipping creation of %d pods, decrementing expectations for %s %s/%s"
                             % (skipped_pods, self._type.kind, rs.metadata.namespace, rs.metadata.name))
                for i in range(skipped_pods):
                    self.expectations.ce.creation_observed(rs_key)
            return
        elif diff > 0:
            if diff > self.burst_replicas:
                diff = self.burst_replicas
            logging.info("Too many replicas, need: %d, deleting: %d", rs.spec.replicas, diff)
            # related_pods = self._get_indirectly_related_pods(rs)
            pods_to_delete = _get_pod_to_delete(filtered_pods, [], diff)
            self.expectations.expect_deletions(rs_key, _get_pod_keys(pods_to_delete))
            # todo 并行
            for pod in pods_to_delete:
                try:
                    self.pod_control.delete_pod(rs.metadata.namespace, pod.metadata.name, rs)
                except Exception as e:
                    pod_key = controller_utils.pod_key(pod)
                    self.expectations.deletion_observed(rs_key, pod_key)
                    if not isinstance(e, errors.ApiException) or not errors.is_not_found(e):
                        logging.warning("failed to delete %s, decremented expectations for %s %s/%s"
                                        % (pod_key, self._type.kind, rs.metadata.namespace, rs.metadata.name))
        else:
            logging.info("no diff replicas for rs rs %s/%s" % (rs.metadata.namespace, rs.metadata.name))

    def _claim_pods(self, rs: IoDragonAppsV1ReplicaSet, selector: labels.Selector, filtered_pods: list) -> list:

        def get_rs():
            fresh = self.kube_client.get(name=rs.metadata.name, namespace=rs.metadata.namespace)
            if fresh.metadata.uid != rs.metadata.uid:
                raise Exception("original %s %s/%s is gone: got uid: %s, wanted %s"
                                % (self._type.kind, rs.metadata.namespace, rs.metadata.name,
                                   fresh.metadata.uid, rs.metadata.uid))
            return fresh
        cm = controller_utils.PodControllerRefManager(self.pod_control,
                                                      rs, selector, self._type,
                                                      controller_utils.recheck_deletion_timestamp(get_rs))
        return cm.claim_pods(filtered_pods)

    def __sync_replicaset(self, key: str):
        namespace, name = cache.split_meta_namespace_key(key)
        rs = None
        try:
            rs = self.rs_lister.with_namespace(namespace).get(name)
        except errors.ApiException as e:
            if errors.is_not_found(e):
                logging.info("%s %s has been deleted" % (self._type.kind, key))
                self.expectations.delete_expectations(key)
                return
        if rs is None:
            logging.error("unexpect error, rs is None")
            return
        rs_need_sync = self.expectations.ce.satisfied_expectations(key)
        try:
            selector = meta_v1.labels_selector_as_selector(rs.spec.selector)
        except IndexError as e:
            logging.error("error converting pod selector to selector for rs %s/%s: %s" % (namespace, name, str(e)))
            return
        all_pods = self.pod_lister.with_namespace(rs.metadata.namespace).list(labels.every_thing)
        filtered_pods = controller_utils.filter_active_pods(all_pods)
        filtered_pods = self._claim_pods(rs, selector, filtered_pods)
        logging.info("all pods: %d, filtered_pods: %d" % (len(all_pods), len(filtered_pods)))
        manage_replica_exception = None
        if rs_need_sync and not rs.metadata.deletion_timestamp:
            try:
                self._manage_replicas(filtered_pods, rs)
            except Exception as e:
                manage_replica_exception = e
        if not rs_need_sync:
            logging.info("rs %s/%s is not needed to sync replicas" % (rs.metadata.namespace, rs.metadata.name))
        rs = copy.deepcopy(rs)
        new_status = replica_set_utils.calculate_status(rs, filtered_pods, manage_replica_exception)
        updated_rs = replica_set_utils.update_replicaset_status(self.kube_client, rs, new_status)
        if manage_replica_exception is None and updated_rs.spec.min_ready_seconds > 0 and \
            updated_rs.status.ready_replicas == updated_rs.spec.replicas and \
            updated_rs.status.available_replicas != updated_rs.spec.replicas:
            self.queue.add_after(key, updated_rs.spec.min_ready_seconds)
        if manage_replica_exception is not None:
            raise manage_replica_exception

    def shut_down(self):
        logging.info("replicaset-controller quit...")
        self.queue.shutdown()
