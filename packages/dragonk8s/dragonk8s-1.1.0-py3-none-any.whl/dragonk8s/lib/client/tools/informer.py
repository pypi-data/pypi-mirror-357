import functools
import logging
import queue
import threading
import time
from threading import Event
from dragonk8s.lib.apimachinery.pkg.apis import meta_v1
from dragonk8s.lib.apimachinery.pkg.runtime import schema
from dragonk8s.lib.client.tools import cache
from dragonk8s.lib.apimachinery.pkg.watch import watch
from dragonk8s.lib.client.tools import pager
from dragonk8s.lib.apimachinery.pkg.api import errors
from kubernetes.client.exceptions import ApiException
from dragonk8s.lib.client.tools import fifo
from dragonk8s.lib.apimachinery.pkg.util import wait
from dragonk8s.lib.client.tools import delta
from queue import Queue
from dragonk8s.lib.pool.thread_manager import GlobalThreadManager


class ResourceEventHandler(object):

    def on_add(self, obj):
        pass

    def on_update(self, old_obj, new_obj):
        pass

    def on_delete(self, obj):
        pass


class ResourceEventHandlerFuncs(ResourceEventHandler):

    def __init__(self, add_func=None, update_func=None, delete_func=None):
        self.add_func = add_func
        self.update_func = update_func
        self.delete_func = delete_func

    def on_add(self, obj):
        if self.add_func:
            self.add_func(obj)

    def on_update(self, old_obj, new_obj):
        if self.update_func:
            self.update_func(old_obj, new_obj)

    def on_delete(self, obj):
        if self.delete_func:
            self.delete_func(obj)


class FilteringResourceEventHandler(ResourceEventHandler):

    def __init__(self, filter_func, handler: ResourceEventHandler):
        self.filter_func = filter_func
        self.handler = handler

    def on_add(self, obj):
        if not self.filter_func(obj):
            return
        self.handler.on_add(obj)

    def on_update(self, old_obj, new_obj):
        newer = self.filter_func(new_obj)
        older = self.filter_func(old_obj)
        if newer and older:
            self.handler.on_update(old_obj, new_obj)
        elif newer and not older:
            self.handler.on_add(new_obj)
        elif not newer and older:
            self.handler.on_delete(old_obj)

    def on_delete(self, obj):
        if not self.filter_func(obj):
            return
        self.handler.on_delete(obj)


class Controller(object):

    def run(self, stop: Event):
        pass

    def has_synced(self) -> bool:
        pass

    def last_sync_resource_version(self) -> str:
        pass


class Lister(object):

    def list(self, options: meta_v1.ListOptions):
        pass


class Watcher(object):

    def watch(self, options: meta_v1.ListOptions) -> watch.Interface:
        pass


class ListerWatcher(Lister, Watcher):
    pass


class ResourceVersionUpdater(object):

    def update_resource_version(self, resource_version: str):
        pass


class Reflector(object):

    def __init__(self, name, lw: ListerWatcher, resync_period=0, store: cache.Store = None, parse_func=None):
        self.name = name
        if not self.name:
            self.name = "inner_controller"
        self.expected_type = None
        self.expected_type_name = ""
        self.expected_gvk = None
        self.store = store
        self.lister_watcher = lw
        # todo
        self.backoff_manager = None
        self.init_conn_backoff_manager = None

        self.resync_period = resync_period
        self.should_resync = None
        self.paginated_result = False
        self.last_sync_resource_version = ""
        self.is_last_sync_resource_version_unavailable = False
        self.last_sync_resource_version_mutex = threading.Lock()
        self.watch_list_page_size = 0
        # todo
        self.watch_error_handler = None
        self.parse_func = parse_func

    def get_last_sync_resource_version(self):
        try:
            self.last_sync_resource_version_mutex.acquire(True)
            return self.last_sync_resource_version
        finally:
            self.last_sync_resource_version_mutex.acquire()

    def set_last_sync_resource_version(self, v: str):
        with self.last_sync_resource_version_mutex:
            self.last_sync_resource_version = v

    def set_last_sync_resource_version_unavailable(self, is_unavailable: bool):
        with self.last_sync_resource_version_mutex:
            self.last_sync_resource_version = is_unavailable

    def _set_expected_type(self, obj):
        self.expected_type = type(obj)
        self.expected_type_name = self.expected_type.__name__
        self.expected_gvk = schema.from_obj(obj)

    def _relist_resource_version(self):
        try:
            self.last_sync_resource_version_mutex.acquire(blocking=True)
            if self.is_last_sync_resource_version_unavailable:
                return ""
            if self.last_sync_resource_version == "":
                return "0"
            return self.last_sync_resource_version
        finally:
            self.last_sync_resource_version_mutex.release()

    def watch_handler(self, start: float, w, resource_version: str, stop: Event):
        new_resource_version = resource_version
        if not w:
            return new_resource_version
        event_count = 0
        while True:
            if stop.is_set():
                return
            event = w.get_result_queue().get(True, 5)
            if event is None:
                continue
            if event['type'] == watch.EventType.End:
                break
            if event['type'] == watch.EventType.Error:
                raise Exception("get error event: " + event['object'].to_str())
            if self.parse_func:
                obj = self.parse_func(event['object'])
            else:
                obj = event['object']
            if self.expected_type:
                if not isinstance(obj, self.expected_type):
                    logging.error("%s expected type %s, but watch event object had type %s" % (
                        self.name, self.expected_type.__name__, type(obj).__name__))
                    continue
            if self.expected_gvk:
                gvk = schema.from_obj(obj)
                if str(self.expected_gvk) != str(gvk):
                    logging.error("%s expected gvk %s, but watch event object had gvk %s" % (
                        self.name, str(self.expected_gvk), str(gvk)))
                    continue
            if not hasattr(obj, "metadata"):
                logging.error("%s: unable to understand watch event: %s" % (self.name, str(event)))
                continue
            new_resource_version = obj.metadata.resource_version
            if event['type'] == watch.EventType.Added:
                self.store.add(obj)
            elif event['type'] == watch.EventType.Modified:
                self.store.update(obj)
            elif event['type'] == watch.EventType.Deleted:
                self.store.delete(obj)
            elif event['type'] == watch.EventType.Bookmark:
                pass
            else:
                logging.error("%s: unable to understand watch event: %s" % (self.name, str(event)))
            self.set_last_sync_resource_version(new_resource_version)

            if hasattr(self.store, "update_resource_version"):
                self.store.update_resource_version(new_resource_version)
            event_count += 1
        watch_duration = time.time() - start
        if watch_duration < 60 and event_count == 0:
            raise Exception(
                "very short watch: %s : Unexpected watch close - watch lasted less than a second and no items received"
                % self.name)
        logging.info("%s: Watch close - %s total %d items received" % (self.name, self.expected_type_name, event_count))
        return new_resource_version

    def _sync_with(self, items, resource_version: str):
        self.store.replace(items, resource_version)

    def list_and_watch(self, stop: Event):
        logging.info("listing and watch %s from %s", self.expected_type_name, self.name)
        resource_version = "0"
        options = meta_v1.ListOptions(
            resource_version=self._relist_resource_version()
        )
        ex = None
        try:
            paginated_result = False
            res_list = None

            page = pager.ListPager(pager.simple_page_func(self.lister_watcher.list))
            if self.watch_list_page_size != 0:
                page.page_size = self.watch_list_page_size
            elif self.paginated_result:
                pass
            elif options.resource_version != "" and options.resource_version != "0":
                page.page_size = 0
            try:
                res_list, paginated_result = page.list(options, stop)
            except ApiException as e:
                logging.error("page list error: %s" % str(e))
                if errors.is_resource_expired(e) or errors.is_too_large_resource_version_error(e):
                    self.set_last_sync_resource_version_unavailable(True)
                    rest_list, paginated_result = page.list(
                        meta_v1.ListOptions(resource_version=self._relist_resource_version()), stop)
        except Exception as e:
            logging.error("%s: failed to list %s: %s", self.name, self.expected_type_name, str(e))
            ex = e
        else:
            if options.resource_version == "0" and paginated_result:
                self.paginated_result = True
            self.set_last_sync_resource_version_unavailable(False)
            if res_list is None or not hasattr(res_list, "metadata"):
                logging.error("unable to understand list result: %s" % str(res_list))
            else:
                try:
                    resource_version = res_list.metadata.resource_version
                    items = res_list.items
                    self._sync_with(items, resource_version)
                    self.set_last_sync_resource_version(resource_version)
                except Exception as e:
                    ex = e
        if ex is not None:
            raise ex

        def resync():
            count = 0
            while not stop.is_set():
                time.sleep(1)
                count += 1
                if count >= self.resync_period:
                    count = 0
                    if self.should_resync is None or (self.should_resync is not None and self.should_resync()):
                        logging.info("%s: forcing resync" % self.name)
                        self.store.resync()

        th = GlobalThreadManager.new_thread(target=resync, generate_name="resync")
        th.start()

        while not stop.is_set():
            timeout_seconds = 1
            options = meta_v1.ListOptions(
                resource_version=resource_version,
                timeout_seconds=timeout_seconds,
                allow_watch_bookmarks=True,
            )
            start = time.time()
            try:
                w = self.lister_watcher.watch(options)
            except ApiException as e:
                if errors.is_too_many_requests(e):
                    time.sleep(1)
                    continue
                else:
                    raise e
            except Exception as e:
                if "Connection refused" in str(e):
                    time.sleep(1)
                    continue
                else:
                    raise e
            else:
                try:
                    new_resource_version = self.watch_handler(start, w, resource_version, stop)
                    resource_version = new_resource_version
                except ApiException as e:
                    if errors.is_resource_expired(e):
                        logging.info("%s: watch of %s closed with: %s" % (self.name, self.expected_type_name, str(e)))
                    elif errors.is_too_many_requests(e):
                        logging.info(
                            "%s: watch of %s returned 429 - backing off" % (self.name, self.expected_type_name))
                        time.sleep(1)
                        continue
                    else:
                        logging.warning("%s: watch of %s ended with: %s" % (self.name, self.expected_type_name, str(e)))
                except TypeError as e:
                    logging.warning(
                        "%s: watch of %s ended with unexpect error: %s" % (self.name, self.expected_type_name, str(e)))
        logging.info("list and watch end...")

    def run(self, stop: Event):
        logging.info("starting reflector %s (%s) from %s", self.expected_type_name, self.resync_period, self.name)

        def do():
            try:
                self.list_and_watch(stop)
            except Exception as e:
                if self.watch_error_handler:
                    self.watch_error_handler(self, e)
                else:
                    raise e

        wait.until_named(do, 5, stop, "reflector run")
        logging.info("stopping reflector %s (%s) from %s", self.expected_type_name, self.resync_period, self.name)


class SharedInformer(object):

    def add_event_handler(self, handler: ResourceEventHandler):
        pass

    def add_event_handler_with_resync_period(self, handler: ResourceEventHandler, resync_period: int):
        pass

    def get_store(self) -> cache.Store:
        pass

    def get_controller(self):
        pass

    def run(self, stop: Event):
        pass

    def has_synced(self) -> bool:
        pass

    def last_sync_resource_version(self) -> str:
        pass

    def set_watch_error_handler(self, handler):
        pass

    def set_transform(self, handler):
        pass


class SharedIndexInformer(SharedInformer):

    def add_indexers(self, indexers: dict):
        pass

    def get_indexer(self) -> cache.Indexer:
        pass


def _new_informer(lw: ListerWatcher, obj_type, resync_period: int,
                  h: ResourceEventHandler, client_state: cache.Store, transformer) -> Controller:
    fifo_queue = delta.DeltaFIFO(delta.DeltaFIFOOptions(
        known_objects=client_state,
        emit_delta_type_replaced=True,
    ))

    def process(obj):
        if isinstance(obj, list):
            _process_deltas(h, client_state, transformer, obj)
        else:
            raise Exception("object given as Process argument is not Deltas")

    cfg = Config(
        queue=fifo_queue,
        lister_watcher=lw,
        full_resync_period=resync_period,
        retry_on_error=False,
        process_func=process,
        obj_type=obj_type
    )
    return InnerController(cfg)


class Config(object):

    def __init__(self, queue: fifo.Queue, lister_watcher: ListerWatcher, process_func, obj_type, full_resync_period=0,
                 should_resync_func=None, retry_on_error=True, watch_error_handler=None, watch_list_page_size=100):
        self.queue = queue
        self.lister_watcher = lister_watcher
        self.process = process_func
        self.obj_type = obj_type
        self.full_resync_period = full_resync_period
        self.should_resync = should_resync_func
        self.retry_on_error = retry_on_error
        self.watch_error_handler = watch_error_handler
        self.watch_list_page_size = watch_list_page_size


class InnerController(Controller):

    def __init__(self, c: Config):
        self.config = c
        self.reflector = None
        # todo: read write lock
        self.reflector_lock = threading.RLock()

    def run(self, stop: Event):
        def quit():
            while not stop.wait():
                continue
            self.config.queue.close()
        GlobalThreadManager.new_thread(target=quit, generate_name="InnerController quit").start()
        r = Reflector("",
                      self.config.lister_watcher,
                      self.config.full_resync_period,
                      self.config.queue)
        r.should_resync = self.config.should_resync
        r.watch_list_page_size = self.config.watch_list_page_size
        if self.config.watch_error_handler:
            r.watch_error_handler = self.config.watch_error_handler
        try:
            self.reflector_lock.acquire()
            self.reflector = r
        finally:
            self.reflector_lock.release()
        t = GlobalThreadManager.new_thread(target=r.run, args=(stop,), generate_name="InnerController-start")
        t.start()
        wait.until_named(self._process_loop, 1, stop, "inner controller run")
        t.join()

    def has_synced(self) -> bool:
        return self.config.queue.has_synced()

    def last_sync_resource_version(self) -> str:
        try:
            self.reflector_lock.acquire()
            if not self.reflector:
                return ""
            return self.reflector.get_last_sync_resource_version()
        finally:
            self.reflector_lock.release()

    def _process_loop(self):
        obj = None
        while True:
            try:
                obj = self.config.queue.pop(self.config.process)
            except fifo.FIFOClosedException:
                return
            except Exception as e:
                if self.config.retry_on_error:
                    self.config.queue.add_if_not_present(obj)


def deletion_handling_meta_namespace_key_func(obj) -> str:
    if isinstance(obj, cache.DeletedFinalStateUnknown):
        return obj.key
    return cache.meta_namespace_key_func(obj)


def _process_deltas(handler: ResourceEventHandler, client_state: cache.Store, transformer, deltas: list):
    for d in deltas:
        obj = d.obj
        if transformer:
            obj = transformer(obj)
        if d.type in {delta.DeltaType.Sync, delta.DeltaType.Replaced, delta.DeltaType.Added, delta.DeltaType.Updated}:
            old, exists = client_state.get(obj)
            if exists:
                handler.on_update(old, obj)
                client_state.update(obj)
            else:
                handler.on_add(obj)
                client_state.add(obj)
        elif d.type == delta.DeltaType.Deleted:
            handler.on_delete(obj)
            client_state.delete(obj)
        else:
            logging.error("unknow delta type: %s" % d.type)


def new_informer(lw: ListerWatcher, obj_type, resync_period, h: ResourceEventHandler) -> (cache.Store, Controller):
    client_state = cache.Cache(key_func=deletion_handling_meta_namespace_key_func, indexers={})
    # todoR
    return client_state, \
           _new_informer(lw, obj_type=obj_type,
                         resync_period=resync_period, h=h, client_state=client_state, transformer=None)


class _UpdateNotification(object):

    def __init__(self, old_obj, new_obj):
        self.old_obj = old_obj
        self.new_obj = new_obj


class _AddNotification(object):

    def __init__(self, new_obj):
        self.new_obj = new_obj


class _DeleteNotification(object):

    def __init__(self, old_obj):
        self.old_obj = old_obj

class _ProcessorListener(object):

    def __init__(self, handler: ResourceEventHandler, requested_resync_period: int, resync_period: int, now: int,
                 buffer_size: int, stop_ch: threading.Event):
        self.handler = handler
        # todo: RingGrowing
        self.pending_notifications = []
        self.requested_resync_period = requested_resync_period
        self.resync_period = resync_period
        self.resync_lock = threading.Lock()
        self.next_resync = 0
        self.determine_next_resync(now)
        self.add_ch = Queue()
        self.stop_ch = stop_ch

    def determine_next_resync(self, now: int):
        with self.resync_lock:
            self.next_resync = now + self.resync_period

    def should_resync(self, now) -> bool:
        with self.resync_lock:
            if self.resync_period == 0:
                return False
            return now >= self.next_resync

    def set_resync_period(self, resync_period):
        with self.resync_lock:
            self.resync_period = resync_period

    def add(self, notification):
        self.add_ch.put_nowait(notification)

    def run(self):

        def f():
            while self.add_ch.qsize() > 0:
                try:
                    item = self.add_ch.get_nowait()
                except queue.Empty:
                    continue
                if not item:
                    continue
                if isinstance(item, _UpdateNotification):
                    self.handler.on_update(item.old_obj, item.new_obj)
                elif isinstance(item, _AddNotification):
                    self.handler.on_add(item.new_obj)
                elif isinstance(item, _DeleteNotification):
                    self.handler.on_delete(item.old_obj)
                else:
                    logging.error("unrecognized notification")

        wait.until_named(f, 1, self.stop_ch, "listener run")


def _determine_resync_period(desired, check: int) ->int:
    if desired == 0:
        return desired
    if check == 0:
        logging.warning("the specified resyncPeriod %d is invalid because this shared informer doesn't support resyncing", desired)
        return check
    if desired < check:
        logging.warning("the specified resyncPeriod %d is being increased to the minimum resyncCheckPeriod %d", desired, check)
        return check
    return desired

class _SharedProcessor(object):

    def __init__(self):
        self.listeners_started = False
        self.listeners_lock = threading.Lock()
        self.listeners = []
        self.syncing_listeners = []

    def add_listener_locked(self, listener: _ProcessorListener):
        self.listeners.append(listener)
        self.syncing_listeners.append(listener)

    def add_listener(self, listener: _ProcessorListener):
        with self.listeners_lock:
            self.add_listener_locked(listener)
            if self.listeners_started:
                wait.until_with_thread(listener.run, 1, listener.stop_ch, "listener run")

    def distribute(self, obj, sync: bool):
        if sync:
            for listener in self.syncing_listeners:
                listener.add(obj)
        else:
            for listener in self.listeners:
                listener.add(obj)

    def run(self, stop: threading.Event):
        with self.listeners_lock:
            for listener in self.listeners:
                wait.until_with_thread(listener.run, 1, listener.stop_ch, "listener run2")
            self.listeners_started = True
        # while not stop.wait(30):
        #     continue
        # with self.listeners_lock:
        #     for listener in self.listeners:
        #         listener.stop_ch.set()

    def should_resync(self) -> bool:
        with self.listeners_lock:
            self.syncing_listeners.clear()
            resync_needed = False
            now = time.time()
            for listener in self.listeners:
                if listener.should_resync(now):
                    resync_needed = True
                    self.syncing_listeners.append(listener)
                    listener.determine_next_resync(now)
            return resync_needed

    def resync_check_period_changed(self, resync_check_period: int):
        for listener in self.listeners:
            resync_period = _determine_resync_period(listener.requested_resync_period, resync_check_period)
            listener.set_resync_period(resync_period)


class _DummyController(Controller):

    def __init__(self, informer: SharedIndexInformer):
        self.informer = informer

    def run(self, stop: Event):
        pass

    def has_synced(self) -> bool:
        return self.informer.has_synced()

    def last_sync_resource_version(self) -> str:
        pass


class _SharedIndexInformer(SharedIndexInformer, ResourceEventHandler):

    def __init__(self, lw: ListerWatcher, example_obj, default_event_handler_resync_period: int, indexers: dict, stop):
        self.indexer = cache.Cache(deletion_handling_meta_namespace_key_func, indexers)
        self.controller = None
        self.processor = _SharedProcessor()
        self.cache_mutation_detector = cache.DummyMutationDetector()
        self.lister_watcher = lw
        self.obj_type = example_obj
        self.resync_check_period = default_event_handler_resync_period
        self.default_event_handler_resync_period = default_event_handler_resync_period
        self.started = False
        self.stopped = False
        self.started_lock = threading.Lock()
        self.block_deltas = threading.Lock()
        self.watch_error_handler = None
        self.transform = None
        self.stopch = stop

    def add_indexers(self, indexers: dict):
        with self.started_lock:
            if self.started:
                raise Exception("informer has already started")
            self.indexer.add_indexers(indexers)

    def get_indexer(self) -> cache.Indexer:
        return self.indexer

    def add_event_handler(self, handler: ResourceEventHandler):
        self.add_event_handler_with_resync_period(handler, self.default_event_handler_resync_period)

    def add_event_handler_with_resync_period(self, handler: ResourceEventHandler, resync_period: int):
        with self.started_lock:
            if self.stopped:
                logging.info("Handler %s was not added to shared informer because it has stopped already", str(handler))
                return
            if resync_period > 0:
                if resync_period < 1:
                    resync_period = 1
                if resync_period < self.resync_check_period:
                    if self.started:
                        logging.warning("resync_period %d is smaller than resync_check_period %d and the informer "
                                        "has already started. changing it to %d"
                                        % (resync_period, self.resync_check_period, self.resync_check_period))
                        resync_period = self.resync_check_period
                    else:
                        self.resync_check_period = resync_period
                        self.processor.resync_check_period_changed(resync_period)
            listener = _ProcessorListener(
                handler, resync_period, _determine_resync_period(resync_period, self.resync_check_period),
                int(time.time()), 1024, self.stopch)
            if not self.started:
                self.processor.add_listener(listener)
                return
            with self.block_deltas:
                self.processor.add_listener(listener)
                for item in self.indexer.list():
                    listener.add(_AddNotification(new_obj=item))

    def get_store(self) -> cache.Store:
        return self.indexer

    def get_controller(self):
        return _DummyController(self)

    def run(self, stop: Event):
        try:
            if self.has_started():
                logging.warning("the sharedIndexInformer has started, run more than once is not allowed")
                return
            fifo = delta.DeltaFIFO(delta.DeltaFIFOOptions(known_objects=self.indexer, emit_delta_type_replaced=True))
            cfg = Config(
                queue=fifo,
                lister_watcher=self.lister_watcher,
                obj_type=self.obj_type,
                full_resync_period=self.resync_check_period,
                retry_on_error=False,
                should_resync_func=self.processor.should_resync,
                process_func=self.handle_deltas,
                watch_error_handler=self.watch_error_handler
            )
            with self.started_lock:
                self.controller = InnerController(c=cfg)
                self.started = True

            t1 = GlobalThreadManager.new_thread(
                target=functools.partial(self.cache_mutation_detector.run, self.stopch),
                generate_name="cache_mutation_detector")
            t2 = GlobalThreadManager.new_thread(
                target=functools.partial(self.processor.run, self.stopch),
                generate_name="processor.run")
            t1.start()
            t2.start()
            self.controller.run(self.stopch)
            t1.join()
            t2.join()
            with self.started_lock:
                self.stopped = True

        except Exception as e:
            logging.error("informer run error: %s", str(e))

    def has_synced(self) -> bool:
        with self.started_lock:
            return self.controller.has_synced()

    def last_sync_resource_version(self) -> str:
        with self.started_lock:
            if not self.controller:
                return ""
            return self.controller.last_sync_resource_version()

    def set_watch_error_handler(self, handler):
        with self.started_lock:
            if self.started:
                raise Exception("informer has already started")
            self.watch_error_handler = handler

    def set_transform(self, handler):
        with self.started_lock:
            if self.started:
                raise Exception("informer has already started")
            self.transform = handler

    def has_started(self) -> bool:
        with self.started_lock:
            return self.started

    def handle_deltas(self, obj):
        with self.block_deltas:
            if isinstance(obj, list):
                _process_deltas(self, self.indexer, self.transform, obj)
                return
            raise Exception("object given as Process argument is not Deltas")

    def on_add(self, obj):
        self.cache_mutation_detector.add_object(obj)
        self.processor.distribute(_AddNotification(new_obj=obj), False)

    def on_update(self, old_obj, new_obj):
        is_sync = False
        if hasattr(new_obj, "metadata") and hasattr(new_obj.metadata, "resource_version"):
            is_sync = new_obj.metadata.resource_version == old_obj.metadata.resource_version
        self.cache_mutation_detector.add_object(new_obj)
        self.processor.distribute(_UpdateNotification(new_obj=new_obj, old_obj=old_obj), is_sync)

    def on_delete(self, obj):
        self.processor.distribute(_DeleteNotification(old_obj=obj), False)


class ListWatch(ListerWatcher):

    def __init__(self, list_func, watch_func, disable_chunking=False):
        self.list_func = list_func
        self.watch_func = watch_func
        self.disable_chunking = disable_chunking

    def list(self, options: meta_v1.ListOptions):
        return self.list_func(options)

    def watch(self, options: meta_v1.ListOptions) -> watch.Interface:
        return self.watch_func(options)
