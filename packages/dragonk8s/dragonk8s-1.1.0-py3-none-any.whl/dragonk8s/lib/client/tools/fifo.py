from threading import Lock, Condition
from dragonk8s.lib.client.tools import cache


class FIFOClosedException(Exception):
    pass


class RequeueException(Exception):

    def __init__(self, e: Exception):
        self.e = e
        super(RequeueException, self).__init__()


class Queue(cache.Store):

    def pop(self, pop_process_func):
        pass

    def add_if_not_present(self, obj):
        pass

    def has_synced(self) -> bool:
        pass

    def close(self):
        pass


def pop_process_func(obj):
    return obj


def pop(queue: Queue):
    return queue.pop(pop_process_func)


class FIFO(Queue):

    def __init__(self, key_func):
        self._lock = Lock()
        self._items = {}
        self._queue = []
        self._populated = False
        self._initial_population_count = 0
        self._key_func = key_func
        self._closed = False
        self._cond = Condition()

    def add(self, obj):
        _id = self._key_func(obj)
        try:
            self._lock.acquire(True)
            self._populated = True
            if _id not in self._items:
                self._queue.append(_id)
            self._items[_id] = obj
            self._cond.notify_all()
        finally:
            self._lock.release()

    def update(self, obj):
        self.add(obj)

    def delete(self, obj):
        _id = self._key_func(obj)
        try:
            self._lock.acquire(True)
            self._populated = True
            if _id in self._items:
                del self._items[_id]
        finally:
            self._lock.release()

    def list(self):
        try:
            self._lock.acquire(True)
            rlist = []
            for k, item in self._items:
                rlist.append(item)
            return rlist
        finally:
            self._lock.release()

    def list_keys(self):
        try:
            self._lock.acquire(True)
            rlist = []
            for k, item in self._items:
                rlist.append(k)
            return rlist
        finally:
            self._lock.release()

    def get(self, obj):
        key = self._key_func(obj)
        return self.get_by_key(key)

    def get_by_key(self, key):
        try:
            self._lock.acquire(True)
            if key not in self._items:
                return None, False
            return self._items[key], True
        finally:
            self._lock.release()

    def is_closed(self) -> bool:
        try:
            self._lock.acquire(True)
            return self._closed
        finally:
            self._lock.release()

    def replace(self, data, resource_version):
        items = {}
        for item in data:
            key = self._key_func(item)
            items[key] = item
        try:
            self._lock.acquire(True)
            if not self._populated:
                self._populated = True
                self._initial_population_count = len(items)
            self._items = items
            self._queue = self._queue[:]
            for key, item in items.items():
                self._queue.append(key)
            if len(self._queue) > 0:
                self._cond.notify_all()
        finally:
            self._lock.release()

    def resync(self):
        try:
            self._lock.acquire(True)
            in_queue = set()
            for key in self._queue:
                in_queue.add(key)
            for key, item in self._items.items():
                if key not in in_queue:
                    self._queue.append(key)
            if len(self._queue) > 0:
                self._cond.notify_all()
        finally:
            self._lock.release()

    def pop(self, pop_process_func):
        try:
            self._lock.acquire(True)
            while True:
                while len(self._queue) == 0:
                    if self._closed:
                        raise FIFOClosedException()
                    self._cond.wait()
                _id = self._queue.pop(0)
                if self._initial_population_count > 0:
                    self._initial_population_count -= 1
                if _id not in self._items:
                    continue
                item = self._items[_id]
                del self._items[_id]
                try:
                    pop_process_func(item)
                except RequeueException as e:
                    self._add_if_not_presetn(_id, item)
                    raise e
                return item
        finally:
            self._lock.release()

    def _add_if_not_presetn(self, _id, obj):
        self._populated = True
        if _id in self._items:
            return
        self._queue.append(_id)
        self._items[_id] = obj
        self._cond.notify_all()

    def add_if_not_present(self, obj):
        _id = self._key_func(obj)
        try:
            self._lock.acquire(True)
            self._add_if_not_presetn(_id, obj)
        finally:
            self._lock.release()

    def has_synced(self) -> bool:
        try:
            self._lock.acquire(True)
            return self._populated and self._initial_population_count == 0
        finally:
            self._lock.release()

    def close(self):
        try:
            self._lock.acquire(True)
            self._closed = True
            self._cond.notify_all()
        finally:
            self._lock.release()
