from __future__ import annotations

import time

from kubernetes.client.models import V1PodCondition, V1PodStatus, V1Pod
from dragonk8s.pkg.api import types

class PodConditionType(object):
    ContainersReady = "ContainersReady"
    PodInitialized = "Initialized"
    PodReady = "Ready"
    PodScheduled = "PodScheduled"


def get_pod_condition_from_list(conditions: list, condition_type: str) -> (int, V1PodCondition|None):
    if not conditions:
        return -1, None
    for i in range(len(conditions)):
        condition = conditions[i]
        if condition.type == condition_type:
            return i, condition
    return -1, None


def get_pod_condition(status: V1PodStatus, condition_type: str) -> (int, V1PodCondition|None):
    if not status:
        return -1, None
    return get_pod_condition_from_list(status.conditions, condition_type)


def get_pod_ready_condition(status: V1PodStatus) -> V1PodCondition|None:
    _, condition = get_pod_condition(status, PodConditionType.PodReady)
    return condition


def is_pod_ready_condition_true(status: V1PodStatus) -> bool:
    condition = get_pod_ready_condition(status)
    return condition is not None and condition.status == types.ConditionTrue


def is_pod_ready(pod: V1Pod) -> bool:
    return is_pod_ready_condition_true(pod.status)


def is_pod_available(pod: V1Pod, min_ready_seconds: int, now: float) -> bool:
    if not is_pod_ready(pod):
        return False
    c = get_pod_ready_condition(pod.status)
    if not c.last_transition_time:
        last_transition_time = 0
    else:
        last_transition_time = c.last_transition_time.timestamp()
    if min_ready_seconds == 0 or (last_transition_time != 0 and last_transition_time+min_ready_seconds < now):
        return True
    return False
