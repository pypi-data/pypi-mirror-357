from __future__ import annotations

import copy
import json
import logging
import threading
import time

from dragonk8s.lib.client.tools import cache
from dragonk8s.lib.client.tools import fifo

class DeltaType(object):
    Added = "Added"
    Updated = "Updated"
    Deleted = "Deleted"
    Replaced = "Replaced"
    Sync = "Sync"


class Delta(object):

    def __init__(self, type: DeltaType, obj):
        self.type = type
        self.obj = obj


class DeltaFIFOOptions(object):

    def __init__(self, known_objects: cache.KeyListerGetter, emit_delta_type_replaced: bool, key_function=None):
        if not key_function:
            key_function = cache.meta_namespace_key_func
        self.key_function = key_function
        self.known_objects = known_objects
        self.emit_delta_type_replaced = emit_delta_type_replaced


class ZoroLengthDeltasObject(Exception):

    def __init__(self):
        super(ZoroLengthDeltasObject, self).__init__("0 length Deltas object; can't get key")


def _is_deletion_dup(a: Delta, b: Delta) -> Delta | None:
    if b.type != DeltaType.Deleted or a.type != DeltaType.Deleted:
        return None
    if isinstance(b, cache.DeletedFinalStateUnknown):
        return a
    return b


def is_dup(a: Delta, b: Delta) -> Delta | None:
    out = _is_deletion_dup(a, b)
    if out is not None:
        return out
    return None


# 如果DeletedFinalStateUnknown是倒数第二个就删掉他
def dedup_deltas(deltas: list) -> list:
    if len(deltas) < 2:
        return deltas
    a = deltas[-1]
    b = deltas[-2]
    out = is_dup(a, b)
    if out is not None:
        deltas[-2] = out
        return deltas[:-1]
    return deltas


class DeltaFIFO(fifo.Queue):

    @staticmethod
    def new_delta_fifo(key_func, known_objects: cache.KeyListerGetter):
        return DeltaFIFO(DeltaFIFOOptions(known_objects, False, key_func))

    def __init__(self, opts: DeltaFIFOOptions):
        if not opts.key_function:
            opts.key_function = cache.meta_namespace_key_func
        self.items = {}
        self.queue = []
        self.key_func = opts.key_function
        self.known_objects = opts.known_objects
        self.emit_delta_type_replaced = opts.emit_delta_type_replaced
        self.lock = threading.Lock()
        self.closed = False
        self.cond = threading.Condition(lock=self.lock)
        self.populated = False
        self.initial_population_count = 0

    def queue_action_locked(self, action_type, obj):
        try:
            id = self.key_of(obj)
        except Exception as e:
            raise cache.KeyError(obj, e)
        old_deltas = self.items[id] if id in self.items else []
        new_deltas = copy.copy(old_deltas)
        new_deltas.append(Delta(action_type, obj))
        new_deltas = dedup_deltas(new_deltas)
        if len(new_deltas) > 0:
            if id not in self.items:
                self.queue.append(id)
            self.items[id] = new_deltas
            self.cond.notify_all()
        else:
            if not old_deltas:
                logging.error("Impossible dedupDeltas for id=%s, old_deltas=%s, obj=%s; ignoring"
                              % (id, json.dumps(old_deltas), json.dumps(obj)))
            logging.error("Impossible dedupDeltas for id=%s, old_deltas=%s, "
                          "obj=%s; breaking invariant by storing empty Deltas"
                          % (id, json.dumps(old_deltas), json.dumps(obj)))
            self.items[id] = new_deltas
            raise Exception("Impossible dedupDeltas for id=%s, old_deltas=%s,obj=%s; "
                            "breaking invariant by storing empty Deltas"
                            % (id, json.dumps(old_deltas), json.dumps(obj)))

    def list_locked(self) -> list:
        l = []
        for key, item in self.items.items():
            l.append(item[-1].obj)
        return l

    def close(self):
        try:
            self.lock.acquire()
            self.closed = True
            self.cond.notify_all()
        finally:
            self.lock.release()

    def is_closed(self) -> bool:
        with self.lock:
            return self.closed

    def key_of(self, obj) -> str:
        if isinstance(obj, list):
            if len(obj) == 0:
                raise cache.KeyError(obj, ZoroLengthDeltasObject())
            obj = obj[-1].obj
        if isinstance(obj, cache.DeletedFinalStateUnknown):
            return obj.key
        return self.key_func(obj)

    def add(self, obj):
        with self.lock:
            self.populated = True
            self.queue_action_locked(DeltaType.Added, obj)

    def update(self, obj):
        with self.lock:
            self.populated = True
            self.queue_action_locked(DeltaType.Updated, obj)

    def delete(self, obj):
        try:
            id = self.key_of(obj)
        except Exception as e:
            raise cache.KeyError(obj, e)
        with self.lock:
            self.populated = True
            if self.known_objects is None:
                if id not in self.items:
                    return
            else:
                try:
                    _, exists = self.known_objects.get_by_key(id)
                except Exception as e:
                    logging.error("known_objects get_by_key error: %s" % str(e))
                else:
                    if not exists and id not in self.items:
                        return
            return self.queue_action_locked(DeltaType.Deleted, obj)

    def list(self):
        with self.lock:
            return self.list_locked()

    def list_keys(self):
        with self.lock:
            l = []
            for key in self.queue:
                l.append(key)
        return l

    def get(self, obj):
        try:
            key = self.key_of(obj)
        except Exception as e:
            raise cache.KeyError(obj, e)
        return self.get_by_key(key)

    def get_by_key(self, key):
        with self.lock:
            if key in self.items:
                return copy.copy(self.items[key])
        return []

    def replace(self, data, resource_version):
        with self.lock:
            keys = set()
            action = DeltaType.Sync
            if self.emit_delta_type_replaced:
                action = DeltaType.Replaced

            for item in data:
                try:
                    key = self.key_of(item)
                except Exception as e:
                    raise cache.KeyError(item, e)
                keys.add(key)
                try:
                    self.queue_action_locked(action, item)
                except Exception as e:
                    raise Exception("couldn't enqueue object: %s", str(e))
            if self.known_objects is None:
                queued_deletions = 0
                for k, old_item in self.items.items():
                    if k in keys:
                        continue
                    deleted_obj = old_item[-1].obj
                    queued_deletions += 1
                    self.queue_action_locked(DeltaType.Deleted, cache.DeletedFinalStateUnknown(k, deleted_obj))
                if not self.populated:
                    self.populated = True
                    self.initial_population_count = len(keys) + queued_deletions
                return

            know_keys = self.known_objects.list_keys()
            queued_deletions = 0
            for k in know_keys:
                if k in keys:
                    continue
                try:
                    deleted_obj, exist = self.known_objects.get_by_key(k)
                except Exception as e:
                    deleted_obj = None
                    logging.error("Unexpected error %s during lookup of key: %s, "
                                  "placing DeleteFinalStateUnkonwn marker without object" % (str(e), k))
                else:
                    if not exist:
                        deleted_obj = None
                        logging.info("key: %s does not exist in konwn objects store, "
                                     "placing DeleteFinalStateUnkonwn marker without object" % k)
                queued_deletions += 1
                self.queue_action_locked(DeltaType.Deleted, cache.DeletedFinalStateUnknown(k, deleted_obj))
            if not self.populated:
                self.populated = True
                self.initial_population_count = len(keys) + queued_deletions

    def _sync_key_locked(self, key: str):
        try:
            obj, exists = self.known_objects.get_by_key(key)
        except Exception as e:
            logging.error("Unexpected error %s during lookup of key %s, unable to queue object for sync" % (str(e), key))
            return
        else:
            if not exists:
                logging.info("key %s does not exist in known objects store, unable to queue object for sync" % key)
                return
        try:
            id = self.key_of(obj)
        except Exception as e:
            raise cache.KeyError(obj, e)
        if len(self.items[id]) > 0:
            return
        try:
            self.queue_action_locked(DeltaType.Sync, obj)
        except Exception as e:
            raise Exception("couldn't queue object: %s" % str(e))
        return

    def resync(self):
        with self.lock:
            if not self.known_objects:
                return
            keys = self.known_objects.list_keys()
            for k in keys:
                self._sync_key_locked(k)

    def pop(self, pop_process_func):
        with self.lock:
            while True:
                while len(self.queue) == 0:
                    if self.closed:
                        raise fifo.FIFOClosedException()
                    self.cond.wait()
                id = self.queue.pop(0)
                depth = len(self.queue)
                if self.initial_population_count > 0:
                    self.initial_population_count -= 1
                if id not in self.items:
                    logging.error("Inconceivable! %s was in queue but not in items" % id)
                    continue
                item = self.items[id]
                del self.items[id]
                start = time.time()
                try:
                    pop_process_func(item)
                except fifo.RequeueException as e:
                    self._add_if_not_present(id, item)
                    raise e.e
                finally:
                    end = time.time()
                    if end - start >= 0.1 and depth > 10:
                        logging.warning("id: %s, depth: %s, slow event handlers blocking the queue" % (id, str(depth)))

                return item

    def _add_if_not_present(self, id: str, deltas: list):
        self.populated = True
        if id in self.items:
            return
        self.queue.append(id)
        self.items[id] = deltas
        self.cond.notify_all()

    def add_if_not_present(self, obj):
        if not isinstance(obj, list):
            raise Exception("obj must be a list of delta, but got: %s", obj.__type__)
        try:
            id = self.key_of(obj)
        except Exception as e:
            raise cache.KeyError(obj, e)
        with self.lock:
            self._add_if_not_present(id, obj)

    def has_synced(self) -> bool:
        with self.lock:
            return self.populated and self.initial_population_count == 0
