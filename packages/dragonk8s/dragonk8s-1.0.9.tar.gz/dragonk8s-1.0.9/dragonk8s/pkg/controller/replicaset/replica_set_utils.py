from __future__ import annotations

import copy
import json
import logging

from dragonk8s.dragon.models import IoDragonAppsV1ReplicaSet, IoDragonAppsV1ReplicaSetStatus, \
    IoDragonAppsV1ReplicaSetStatusConditions, IoDragonAppsV1ReplicaSetSpec, IoDragonAppsV1JobSpecTemplateSpec
from kubernetes.client.models import V1Pod
from dragonk8s.lib.apimachinery.pkg import labels
from dragonk8s.pkg.api.v1 import pod_util
import time
from dragonk8s.pkg.api import types
from dragonk8s.lib.util import timeutil


class ReplicaSetConditionType(object):
    ReplicaSetReplicaFailure = "ReplicaFailure"


def get_condition(status: IoDragonAppsV1ReplicaSetStatus, cond_type: str) -> IoDragonAppsV1ReplicaSetStatusConditions|None:
    if not status:
        return None
    if not status.conditions:
        return None
    for c in status.conditions:
        if c.type == cond_type:
            return c
    return None


def new_replication_condition(cond_type, status, reason, msg) -> IoDragonAppsV1ReplicaSetStatusConditions:
    return IoDragonAppsV1ReplicaSetStatusConditions(
        type=cond_type,
        status=status,
        last_transition_time=timeutil.to_time_str_with_ns(time.time()),
        reason=reason,
        message=msg,
    )


def _filter_out_condition(conditions, cond_type) -> list:
    new_conds = []
    for c in conditions:
        if c.type == cond_type:
            continue
        new_conds.append(c)
    return new_conds


def set_condition(status: IoDragonAppsV1ReplicaSetStatus, condition: IoDragonAppsV1ReplicaSetStatusConditions):
    current_cond = get_condition(status, condition.type)
    if current_cond is not None and current_cond.status == condition.status and current_cond.reason == condition.reason:
        return
    new_cond = _filter_out_condition(status.conditions, condition.type)
    new_cond.append(condition)
    status.conditions = new_cond


def remove_condition(status: IoDragonAppsV1ReplicaSetStatus, cond_type):
    status.conditions = _filter_out_condition(status.conditions, cond_type)


def calculate_status(rs: IoDragonAppsV1ReplicaSet,
                     filtered_pods: list, manage_replicas_exception: Exception) -> IoDragonAppsV1ReplicaSetStatus:
    new_status = copy.deepcopy(rs.status)
    if new_status is None:
        new_status = IoDragonAppsV1ReplicaSetStatus()
    fully_labeled_replicas_count = 0
    ready_replicas_count = 0
    available_replicas_count = 0
    template_label = labels.selector_from_validated_set(labels.Set(rs.spec.template.metadata.labels))
    for pod in filtered_pods:
        if template_label.matches(labels.Set(pod.metadata.labels)):
            fully_labeled_replicas_count += 1
        if pod_util.is_pod_ready(pod):
            ready_replicas_count += 1
            if pod_util.is_pod_available(pod, rs.spec.min_ready_seconds, time.time()):
                available_replicas_count += 1
    failure_cond = get_condition(rs.status, ReplicaSetConditionType.ReplicaSetReplicaFailure)
    if manage_replicas_exception is not None and failure_cond is not None:
        reason = ""
        diff = len(filtered_pods) - int(rs.status.replicas)
        if diff < 0:
            reason = "FailedCreate"
        else:
            reason = "FailedDelete"
        cond = new_replication_condition(ReplicaSetConditionType.ReplicaSetReplicaFailure,
                                         types.ConditionTrue, reason, str(manage_replicas_exception))

        set_condition(new_status, cond)
    elif manage_replicas_exception is None and failure_cond is not None:
        remove_condition(new_status, ReplicaSetConditionType.ReplicaSetReplicaFailure)

    new_status.replicas = len(filtered_pods)
    new_status.fully_labeled_replicas = fully_labeled_replicas_count
    new_status.ready_replicas = ready_replicas_count
    new_status.available_replicas = available_replicas_count
    return new_status


def update_replicaset_status(client, rs: IoDragonAppsV1ReplicaSet, new_status: IoDragonAppsV1ReplicaSetStatus) -> IoDragonAppsV1ReplicaSet:
    if rs.status is not None and new_status is not None and rs.status.replicas == new_status.replicas and \
            rs.status.fully_labeled_replicas == new_status.fully_labeled_replicas and \
            rs.status.ready_replicas == new_status.ready_replicas and \
            rs.status.available_replicas == new_status.available_replicas and \
            rs.metadata.generation == rs.status.observed_generation and \
            rs.status.conditions == new_status.conditions:
        logging.debug("no status changed for rs %s/%s" % (rs.metadata.namespace, rs.metadata.name))
        return rs
    if new_status is None:
        new_status = IoDragonAppsV1ReplicaSetStatus()
    new_status.observed_generation = rs.metadata.generation
    logging.info("Updating status for %s: %s/%s, status: %s"
                 % (rs.kind, rs.metadata.namespace, rs.metadata.name, json.dumps(new_status.to_dict())))
    rs.status = new_status
    return client.status.replace(name=rs.metadata.name, namespace=rs.metadata.namespace, body=rs)
