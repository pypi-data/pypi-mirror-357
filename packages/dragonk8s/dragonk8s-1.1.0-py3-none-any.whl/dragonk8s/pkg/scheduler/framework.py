from dragonk8s.lib.apimachinery.pkg import labels
from kubernetes.client.models import V1Pod


class AffinityTerm(object):

    def __init__(self, selector: labels.Selector = None, topology_key: str = "",
                 namespace_selector: labels.Selector = None):
        self.namesapces = set()
        self.selector = selector
        self.topology_key = topology_key
        self.namespace_selector = namespace_selector

    def matches(self, pod: V1Pod, ns_labels: labels.Set) -> bool:
        if pod.metadata.namespace in self.namesapces or self.namespace_selector.matches(ns_labels):
            return self.selector.matches(labels.Set(pod.metadata.labels))
        return False


class WeightedAffinityTerm(AffinityTerm):

    def __init__(self, weight, selector: labels.Selector = None, topology_key: str = "",
                 namespace_selector: labels.Selector = None):
        super(WeightedAffinityTerm, self).__init__(selector, topology_key, namespace_selector)
        self.weight = weight


class PodInfo(object):

    def __init__(self):
        self.pod = None
        self.required_affinity_terms = []
        self.required_anti_affinity_terms = []
        self.preferred_affinity_terms = []
        self.preferred_anti_affinity_terms = []

    def update(self, pod: V1Pod):
        if pod is not None and self.pod is not None and self.pod.metadata.uid == pod.metadata.uid:
            self.pod = pod
            return
        if pod is None:
            return
        from kubernetes.client.models import V1PodAffinity
        affinity = pod.spec.affinity
        if affinity:
            if affinity.pod_affinity:
                self.preferred_affinity_terms = \
                    affinity.pod_affinity.preferred_during_scheduling_ignored_during_execution
            if affinity.pod_anti_affinity:
                self.preferred_anti_affinity_terms \
                    = affinity.pod_anti_affinity.preferred_during_scheduling_ignored_during_execution

        # todo