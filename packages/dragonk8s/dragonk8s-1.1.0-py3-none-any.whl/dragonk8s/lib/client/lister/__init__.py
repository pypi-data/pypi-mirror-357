import logging

from dragonk8s.lib.apimachinery.pkg.labels import Selector, Set
from dragonk8s.lib.client.tools import cache
from kubernetes.client.models import V1ObjectMeta
from dragonk8s.lib.apimachinery.pkg.api import errors
from dragonk8s.lib.apimeta import apigvk


NamespaceIndex = "namespace"


def list_all(store: cache.Store, selector: Selector, append_fun):
    select_all = selector.empty()
    for m in store.list():
        if select_all:
            append_fun(m)
            continue
        metadata = m.metadata
        if selector.matches(labels=Set(data=metadata.labels)):
            append_fun(m)


def list_all_by_namespace(indexer: cache.Indexer, namespace: str, selector: Selector, append_fun):
    select_all = selector.empty()
    if namespace == "":
        for m in indexer.list():
            if select_all:
                append_fun(m)
                continue
            metadata = m.metadata
            if selector.matches(labels=Set(data=metadata.labels)):
                append_fun(m)
        return
    try:
        items = indexer.index(NamespaceIndex, V1ObjectMeta(namespace=namespace))
    except Exception as e:
        logging.warning("can not retrieve list of objects using index: %s" % str(e))
        for m in indexer.list():
            metadata = m.metadata
            if metadata.namespace == namespace and selector.matches(Set(data=metadata.labels)):
                append_fun(m)
        return
    else:
        for m in items:
            if select_all:
                append_fun(m)
                continue
            metadata = m.metadata
            if selector.matches(Set(data=metadata.labels)):
                append_fun(m)


class INamespaceLister(object):

    def list(self, selector: Selector) -> list:
        pass

    def get(self, name: str):
        pass


class ILister(object):

    def list(self, selector: Selector) -> list:
        pass

    def with_namespace(self, namespace: str) -> INamespaceLister:
        pass


class NamespaceLister(INamespaceLister):

    def __init__(self, indexer: cache.Indexer, namespace: str):
        self.indexer = indexer
        self.namespace = namespace

    def list(self, selector: Selector) -> list:
        ret = []
        list_all_by_namespace(self.indexer, self.namespace, selector, lambda o: ret.append(o))
        return ret

    def get(self, name: str):
        obj, exists = self.indexer.get_by_key("{}/{}".format(self.namespace, name))
        if not exists:
            raise errors.new_not_found(apigvk.IoDragonAppsV1ReplicaSet, name)
        return obj


class Lister(ILister):

    def __init__(self, indexer: cache.Indexer):
        self.indexer = indexer

    def list(self, selector: Selector) -> list:
        ret = []
        list_all(self.indexer, selector, lambda m: ret.append(m))
        return ret

    def with_namespace(self, namespace: str) -> INamespaceLister:
        return NamespaceLister(indexer=self.indexer, namespace=namespace)
