from dragonk8s.lib.client.tools import informer, cache
from dragonk8s.lib.apimeta import apigvk
from dragonk8s.lib.apimachinery.pkg.apis import meta_v1
from dragonk8s.lib.client import CommonWatch
from dragonk8s.lib.client import lister
from kubernetes.client.models import V1Pod
from dragonk8s.lib.apimachinery.pkg import labels
from dragonk8s.lib.client.informers import factory
from dragonk8s.lib.client.informers.informer import BaseInformer


class ReplicaSetLister(lister.Lister):

    def __init__(self, indexer: cache.Indexer):
        super(ReplicaSetLister, self).__init__(indexer)

    def get_pod_replica_sets(self, pod: V1Pod) -> list:
        if len(pod.metadata.labels) == 0:
            raise Exception("no Replicasets found for pod: %s because it has no labels" % pod.metadata.name)
        l = self.with_namespace(pod.metadata.namespace).list(labels.every_thing)
        rss = []
        for rs in l:
            if rs.metadata.namespace != pod.metadata.namespace:
                continue
            selector = meta_v1.labels_selector_as_selector(rs.spec.selector)
            if selector.empty() or not selector.matches(labels.Set(pod.metadata.labels)):
                continue
            rss.append(rs)
        if len(rss) == 0:
            raise Exception("could not find ReplicaSet for pod: %s in namespace %s with labels: %s"
                            % (pod.metadata.name, pod.metadata.namespace, pod.metadata.labels))
        return rss


class ReplicaSetInformer(BaseInformer):

    def __init__(self, informer_factory: factory.SharedInformerFactory, tweak_list_options=None):
        super(ReplicaSetInformer, self).__init__(apigvk.IoDragonAppsV1ReplicaSet, informer_factory, tweak_list_options)

    def lister(self):
        return ReplicaSetLister(indexer=self.informer().get_indexer())
