import json
import logging
import threading
from dragonk8s.lib.apimachinery.pkg.util import wait


class KeyLister(object):

    def list_keys(self) -> list:
        return []


class KeyGetter(object):

    def get_by_key(self, key: str) -> (object, bool):
        return None, False


class KeyListerGetter(KeyLister, KeyGetter):
    pass


class Store(KeyListerGetter):

    def add(self, obj):
        pass

    def update(self, obj):
        pass

    def delete(self, obj):
        pass

    def list(self):
        pass

    def list_keys(self):
        pass

    def get(self, obj):
        pass

    def get_by_key(self, key):
        pass

    def replace(self, data, resource_version):
        pass

    def resync(self):
        pass


class Indexer(Store):
    def index(self, index_name, obj):
        pass

    def index_keys(self, index_name, indexed_value):
        pass

    def list_index_func_values(self, index_name):
        pass

    def by_index(self, index_name, indexed_value):
        pass

    def get_indexers(self):
        pass

    def add_indexers(self, new_indexers):
        pass


class ThreadSafeStore(object):

    def add(self, key, obj):
        pass

    def update(self, key, obj):
        pass

    def delete(self, key, obj):
        pass

    def get(self, key):
        pass

    def list(self):
        pass

    def list_keys(self):
        pass

    def replace(self, items: dict, resource_version: str):
        pass

    def index(self, index_name, obj):
        pass

    def index_keys(self, index_name, indexed_value):
        pass

    def list_index_func_values(self, index_name):
        pass

    def by_index(self, index_name, indexed_value):
        pass

    def get_indexers(self):
        pass

    def add_indexers(self, new_indexers):
        pass

    def resync(self):
        pass


def meta_namespace_key_func(obj):
    if isinstance(obj, str):
        return obj
    if hasattr(obj, "metadata"):
        meta = obj.metadata
        if len(meta.namespace) > 0:
            return "{}/{}".format(meta.namespace, meta.name)
        return meta.name
    raise Exception("object has no meta")


def split_meta_namespace_key(key: str):
    parts = key.split("/")
    l = len(parts)
    if l == 1:
        return "", parts[0]
    if l == 2:
        return parts[0], parts[1]
    raise Exception("unexpected key format: %s" % key)


class ThreadSafeMap(ThreadSafeStore):

    def __init__(self, indexers: dict, indices: dict):
        super().__init__()
        self._lock = threading.Lock()
        self._items = dict()
        self._indexers = indexers
        self._indices = indices

    def _delete_key_from_index(self, key: str, index_value: str, index: dict):
        if index_value not in index:
            return
        s = index[index_value]
        if key in s:
            s.remove(key)
        if len(s) == 0:
            del index[index_value]

    def add_key_to_index(self, key: str, index_value: str, index: dict):
        if index_value not in index:
            index[index_value] = set()
        index[index_value].add(key)

    def _update_indices(self, old_obj, new_obj, key: str):
        old_index_values = []
        index_values = []
        for name, index_func in self._indexers.items():
            if old_obj is not None:
                old_index_values = index_func(old_obj)
            else:
                old_index_values.clear()
            if new_obj is not None:
                index_values = index_func(new_obj)
            else:
                index_values.clear()

            if name not in self._indices:
                self._indices[name] = dict()

            index = self._indices[name]

            if len(index_values) == 1 and len(old_index_values) == 1 and index_values[0] == old_index_values[0]:
                continue

            for value in old_index_values:
                self._delete_key_from_index(key, value, index)

            for value in index_values:
                self.add_key_to_index(key, value, index)

    def add(self, key, obj):
        self.update(key, obj)

    def update(self, key, obj):
        try:
            self._lock.acquire(True)
            old_obj = None
            if key in self._items:
                old_obj = self._items[key]
            self._items[key] = obj
            self._update_indices(old_obj, obj, key)
        finally:
            self._lock.release()

    def delete(self, key, obj):
        try:
            self._lock.acquire(True)
            if key in self._items:
                self._update_indices(obj, None, key)
                del self._items[key]
        finally:
            self._lock.release()

    def get(self, key):
        try:
            self._lock.acquire(True)
            if key in self._items:
                return self._items[key], True
            return None, False
        finally:
            self._lock.release()

    def list(self):
        try:
            self._lock.acquire(True)
            return self._items.values()
        finally:
            self._lock.release()

    def list_keys(self):
        with self._lock:
            return self._items.keys()

    def replace(self, items: dict, resource_version: str):
        try:
            self._lock.acquire(True)
            self._items = items
            self._indices = dict()
            for key, item in self._items.items():
                self._update_indices(None, item, key)
        finally:
            self._lock.release()

    def _get_index_func(self, index_name):
        if index_name not in self._indexers:
            raise Exception("Index with name %s does not exist" % index_name)
        return self._indexers[index_name]

    def index(self, index_name, obj):
        try:
            self._lock.acquire(True)
            index_func = self._get_index_func(index_name)
            indexed_values = index_func(obj)
            index = self._indices[index_name]
            store_key_set = {}
            if len(indexed_values) == 1:
                store_key_set = index[indexed_values[0]]
            else:
                for indexed_value in indexed_values:
                    for key in index[indexed_value]:
                        store_key_set.add(key)
            return [self._items[store_key] for store_key in store_key_set]
        finally:
            self._lock.release()

    def index_keys(self, index_name, indexed_value):
        try:
            self._lock.acquire(True)
            index_func = self._get_index_func(index_name)
            index = self._indices[index_name]
            if indexed_value not in index:
                return []
            s = index[indexed_value]
            return list(s)
        finally:
            self._lock.release()

    def list_index_func_values(self, index_name):
        try:
            self._lock.acquire(True)
            if index_name not in self._indices:
                return []
            index = self._indices[index_name]
            return index.keys()
        finally:
            self._lock.release()

    def by_index(self, index_name, indexed_value):
        try:
            self._lock.acquire(True)
            index_func = self._get_index_func(index_name)
            index = self._indices[index_name]
            if indexed_value not in index:
                return []
            s = index[indexed_value]
            return [self._items[key] for key in s]
        finally:
            self._lock.release()

    def get_indexers(self):
        return self._indexers

    def add_indexers(self, new_indexers):
        try:
            self._lock.acquire(True)
            if len(self._items) > 0:
                raise Exception("cannot add indexers to running index")
            old_keys = self._indexers.keys()
            new_keys = new_indexers.keys()
            for new_key in new_keys:
                if new_key in old_keys:
                    raise Exception("indexer conflict: %s" % new_key)

            for k, v in new_indexers.items():
                self._indexers[k] = v

        finally:
            self._lock.release()

    def resync(self):
        # nothing to do
        pass


class Cache(Indexer):

    def __init__(self, key_func, indexers: dict):
        super().__init__()
        self._key_func = key_func
        self._cache_storage = ThreadSafeMap(indexers, {})

    @classmethod
    def new_Store(cls, key_func):
        return cls(key_func, {})

    @classmethod
    def new_indexer(cls, key_func, indexers: dict):
        return cls(key_func, indexers)

    def add(self, obj):
        key = self._key_func(obj)
        self._cache_storage.add(key, obj)

    def update(self, obj):
        key = self._key_func(obj)
        self._cache_storage.update(key, obj)

    def delete(self, obj):
        key = self._key_func(obj)
        self._cache_storage.delete(key, obj)

    def list(self):
        return self._cache_storage.list()

    def list_keys(self):
        return self._cache_storage.list_keys()

    def get(self, obj):
        key = self._key_func(obj)
        return self.get_by_key(key)

    def get_by_key(self, key):
        return self._cache_storage.get(key)

    def replace(self, data, resource_version):
        items = {}
        for item in data:
            key = self._key_func(item)
            items[key] = item
        self._cache_storage.replace(items, resource_version)

    def resync(self):
        pass

    def index(self, index_name, obj):
        return self._cache_storage.index(index_name, obj)

    def index_keys(self, index_name, indexed_value):
        return self._cache_storage.index_keys(index_name, indexed_value)

    def list_index_func_values(self, index_name):
        return self._cache_storage.list_index_func_values(index_name)

    def by_index(self, index_name, indexed_value):
        self._cache_storage.by_index(index_name, indexed_value)

    def get_indexers(self):
        return self._cache_storage.get_indexers()

    def add_indexers(self, new_indexers):
        self._cache_storage.add_indexers(new_indexers)


class DeletedFinalStateUnknown(object):

    def __init__(self, key, obj=None):
        self.key = key
        self.obj = obj


class KeyError(Exception):

    def __init__(self, obj, e: Exception):
        self.e = e
        self.obj = obj
        objstr = json.dumps(obj)
        super(KeyError, self).__init__("couldn't create key for object: %s: %s", objstr, str(e))

    def unwrap(self) -> Exception:
        return self.e


class MutationDetector(object):

    def add_object(self, obj):
        pass

    def run(self, stop: threading.Event):
        pass


class DummyMutationDetector(MutationDetector):
    pass


def wait_for_cache_sync(stop: threading.Event, *cache_syncs) -> bool:
    def sync():
        for s in cache_syncs:
            if not s():
                return False
        return True
    try:
        ok = wait.poll(sync, 1, 0, stop, immadiate=True)
        # todo
    except Exception as e:
        logging.error("wait poll failed: %s" % str(e))
        return False
    if not ok:
        logging.info("caches no populated")
        return False
    logging.info("caches populated")
    return True


def wait_for_named_cache_sync(controller_name: str, stop: threading.Event, *cache_syncs) -> bool:
    logging.info("Waiting for caches to sync for %s" % controller_name)
    if not wait_for_cache_sync(stop, *cache_syncs):
        logging.error("unable to sync caches for %s" % controller_name)
        return False
    logging.info("Caches are synced for %s" % controller_name)
    return True



NamespaceIndex = "namespace"


def meta_namespace_index_func(obj) -> list:
    if hasattr(obj, "namespace"):
        metadata = obj
    else:
        metadata = obj.metadata
    return [metadata.namespace]
