import logging
import threading

from dragonk8s.lib.client.tools import informer, cache
from dragonk8s.lib.apimeta import apigvk
from dragonk8s.lib.apimachinery.pkg.apis import meta_v1
from dragonk8s.lib.client import CommonWatch
from dragonk8s.lib.pool.thread_manager import GlobalThreadManager


def new_filtered_informer(
        client, gvk: apigvk.GVK, namespace: str, resync_period:int, indexers: dict, tweak_list_options, stop) -> informer.SharedIndexInformer:
    client = apigvk.get_resource_client(client, gvk)

    def _list_func(options: meta_v1.ListOptions) -> list:
        if tweak_list_options:
            tweak_list_options(options)
        return client.list(namespace=namespace, **options.to_params())

    def _watch_func(options: meta_v1.ListOptions):
        if tweak_list_options:
            tweak_list_options(options)
        return client.watch(namespace=namespace, watcher=CommonWatch(client), **options.to_params())
    return informer._SharedIndexInformer(
        lw=informer.ListWatch(list_func=_list_func, watch_func=_watch_func),
        example_obj=gvk.response_type,
        default_event_handler_resync_period=resync_period,
        indexers=indexers,
        stop=stop
    )


def new_informer(client, gvk: apigvk.GVK, namespace: str, resync_period:int, indexers: dict, stop) -> informer.SharedIndexInformer:
    return new_filtered_informer(client, gvk, namespace, resync_period, indexers, tweak_list_options=None, stop=stop)


class SharedInformerFactory(object):

    def __init__(self, client, default_resync, namespace="", tweak_list_options=None, stop=None):
        self.client = client
        self.default_resync = default_resync
        self.namespace = namespace
        self.tweak_list_options = tweak_list_options
        self.informers = {}
        self.started_informers = {}
        self._custom_resync = {}
        self._lock = threading.Lock()
        self.stop = stop

    def start(self, stop: threading.Event):
        with self._lock:
            for informer_type, ifm in self.informers.items():
                if informer_type not in self.started_informers:
                    logging.info("start informer for %s" % informer_type)
                    th = GlobalThreadManager.new_thread(target=ifm.run, args=(stop, ), name="informer-%s" % informer_type)
                    th.start()
                    self.started_informers[informer_type] = th

    def informer_for(self, gvk: apigvk.GVK, **kwargs) -> informer.SharedIndexInformer:
        with self._lock:
            informer_type = gvk.response_type
            if informer_type in self.informers:
                return self.informers[informer_type]
        resync_period = self.default_resync
        if informer_type in self._custom_resync:
            resync_period = self._custom_resync[informer_type]
        if "indexers" in kwargs:
            indexers = kwargs["indexers"]
        else:
            indexers = {}
        namespace = self.namespace
        if "namespace" in kwargs:
            namespace = kwargs["namespace"]
        tweak_list_options = None
        if "tweak_list_options" in kwargs:
            tweak_list_options = kwargs["tweak_list_options"]
        ifm = new_filtered_informer(client=self.client,
                                    gvk=gvk,
                                    resync_period=resync_period,
                                    indexers=indexers,
                                    tweak_list_options=tweak_list_options,
                                    namespace=namespace,
                                    stop=self.stop)

        self.informers[informer_type] = ifm
        return ifm

    def wait_for_cache_sync(self, stop: threading.Event) -> dict:
        with self._lock:
            informers = {}
            for informer_type, ifm in self.informers.items():
                if informer_type in self.started_informers:
                    informers[informer_type] = ifm
            res = {}
            for informer_type, ifm in informers.items():
                res[informer_type] = cache.wait_for_cache_sync(stop, ifm.has_synced)
            return res

    def set_custom_resync(self, resync_config: dict):
        self._custom_resync = resync_config
