from dragonk8s.lib.client.informers import factory
from dragonk8s.lib.client.tools import informer, cache
from dragonk8s.lib.client import lister
from dragonk8s.lib.apimeta import apigvk


class BaseInformer(object):

    def __init__(self, gvk: apigvk.GVK, informer_factory: factory.SharedInformerFactory, tweak_list_options=None):
        self.factory = informer_factory
        self.tweak_list_options = tweak_list_options
        self.gvk = gvk

    def informer(self) -> informer.SharedIndexInformer:
        return self.factory.informer_for(self.gvk,
                                         indexers={cache.NamespaceIndex: cache.meta_namespace_index_func},
                                         tweak_list_options=self.tweak_list_options)

    def lister(self):
        return lister.Lister(indexer=self.informer().get_indexer())


def get_informer(
        gvk: apigvk.GVK, informer_factory: factory.SharedInformerFactory, tweak_list_options=None) -> BaseInformer:
    return BaseInformer(gvk, informer_factory, tweak_list_options)
