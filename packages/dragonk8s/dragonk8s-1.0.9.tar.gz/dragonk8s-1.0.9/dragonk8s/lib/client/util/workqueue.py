from __future__ import annotations

import logging
import queue
import threading
import time
from dragonk8s.lib.pool.thread_manager import GlobalThreadManager


class Interface(object):

    def add(self, item):
        pass

    def len(self) -> int:
        pass

    def get(self) -> (object, bool):
        pass

    def done(self, item):
        pass

    def shutdown(self):
        pass

    def shutdown_with_drain(self):
        pass

    def shutting_down(self):
        pass


class Type(Interface):

    def __init__(self, update_period=0.5):
        self.queue = []
        self.dirty = set()
        self.processing = set()
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self._shutting_down = False
        self._drain = False
        self.unfinished_work_update_period = update_period

    def add(self, item):
        with self.lock:
            if self._shutting_down:
                return
            if item in self.dirty:
                return
            self.dirty.add(item)
            if item in self.processing:
                return
            self.queue.append(item)
            self.cond.notify(1)

    def len(self) -> int:
        with self.lock:
            return len(self.queue)

    def get(self) -> (object, bool):
        with self.lock:
            while len(self.queue) == 0 and not self._shutting_down:
                self.cond.wait()
            if len(self.queue) == 0:
                return None, True
            item = self.queue.pop(0)
            self.processing.add(item)
            self.dirty.remove(item)
            return item, False

    def done(self, item):
        with self.lock:
            self.processing.remove(item)
            if item in self.dirty:
                self.queue.append(item)
                self.cond.notify(1)
            elif len(self.processing) == 0:
                self.cond.notify(1)

    def set_drain(self, should_drain):
        with self.lock:
            self._drain = should_drain

    def should_drain(self):
        with self.lock:
            return self._drain

    def _shutdown(self):
        with self.lock:
            self._shutting_down = True
            self.cond.notify_all()

    def shutdown(self):
        self.set_drain(False)
        self._shutdown()

    def _is_processing(self) -> bool:
        with self.lock:
            return len(self.processing) != 0

    def _wait_for_processing(self):
        with self.lock:
            if len(self.processing) == 0:
                return
            self.cond.wait()

    def shutdown_with_drain(self):
        self.set_drain(True)
        self._shutdown()
        while self._is_processing() and self.should_drain():
            self._wait_for_processing()

    def shutting_down(self):
        with self.lock:
            return self._shutting_down


class DelayingInterface(Type):

    def add_after(self, item, duration: int):
        pass


class _WaitFor(object):

    def __init__(self, data, ready_at):
        self.data = data
        self.ready_at = ready_at
        self.index = 0

    def __repr__(self):
        return "data: %s, ready_at: %f" % (self.data, self.ready_at)

    def __str__(self):
        return self.__repr__()


class _PriorityQueue(object):

    def __init__(self, size=1000):
        self._data = [_WaitFor(None, 0)] * size
        self._size = size
        self._len = 0

    def is_full(self):
        return self._len == self._size

    def is_empty(self):
        return self._len == 0

    def add(self, x: _WaitFor):
        if self.is_full():
            raise Exception("is full")
        i = self._len
        self._len += 1
        while i > 0:
            p = int((i-1)/2)
            if self._data[p].ready_at <= x.ready_at:
                break
            self._data[i] = self._data[p]
            i = p
        self._data[i] = x
        x.index = i

    def remove(self, x: _WaitFor):
        i = 0
        while i < self._len:
            if self._data[i].data == x.data:
                self._data[i] = self.data[self._len-1]
                self._len -= 1
                break

    def get(self) -> _WaitFor|None:
        if self.is_empty():
            return None
        res = self._data[0]
        i = 0
        x = self._data[self._len-1]
        self._len -= 1
        while 2 * i + 1 < self._len:
            a = 2 * i + 1
            b = 2 * i + 2
            if b < self._len and self._data[b].ready_at < self._data[a].ready_at:
                a = b
            if x.ready_at < self._data[a].ready_at:
                break
            self._data[i] = self._data[a]
            i = a
        self._data[i] = x
        return res

    def peek(self):
        if self.is_empty():
            return None
        return self._data[0]

    @property
    def data(self):
        return self._data[:self._len]

    def __len__(self):
        return self._len


class DelayingType(DelayingInterface):

    def __init__(self):
        self.stop = threading.Event()
        self.heartbeat = 10
        self.waiting_for_addch = queue.Queue(maxsize=1000)
        super(DelayingType, self).__init__()
        GlobalThreadManager.new_thread(target=self._waiting_loop, generate_name="DelayingType-_waiting_loop").start()

    def add_after(self, item, duration: int):
        if self.shutting_down():
            return
        if duration <= 0:
            self.add(item)
            return
        wf = _WaitFor(data=item, ready_at=time.time()+duration)
        try:
            self.waiting_for_addch.put(wf, block=False)
        except queue.Full:
            logging.error("put failed in add_after")

    def shutdown(self):
        if not self.stop.is_set():
            logging.info("DelayingType shutdown...")
            super(DelayingType, self).shutdown()
            self.stop.set()
            logging.error("DelayingType shutdown done...")

    def _waiting_loop(self):
        try:
            waiting_queue = _PriorityQueue()
            waiting = {}
            next_ready = None
            heartbeat = None
            wait_interval = 10
            while True:
                if self.shutting_down():
                    logging.info("quit _waiting_loop...")
                    return
                now = time.time()
                heartbeat = now + wait_interval
                while len(waiting_queue) > 0:
                    entry = waiting_queue.peek()
                    if entry.ready_at > now:
                        break
                    entry = waiting_queue.get()
                    self.add(entry.data)
                    del waiting[entry.data]

                if len(waiting_queue) > 0:
                    entry = waiting_queue.peek()
                    next_ready = entry.ready_at

                waiting_entry = None
                while waiting_entry is None:
                    if self.shutting_down():
                        break
                    try:
                        waiting_entry = self.waiting_for_addch.get(block=True, timeout=2)
                    except queue.Empty:
                        if next_ready is not None and next_ready < time.time():
                            break
                        if heartbeat is not None and heartbeat < time.time():
                            break
                        continue
                if waiting_entry is None:
                    continue
                if waiting_entry.ready_at > time.time():
                    if waiting_entry.data in waiting:
                        existing = waiting[waiting_entry.data]
                        existing.ready_at = waiting_entry.ready_at
                        waiting_queue.remove(existing)
                        waiting_queue.add(existing)
                    else:
                        waiting_queue.add(waiting_entry)
                        waiting[waiting_entry.data] = waiting_entry
                else:
                    self.add(waiting_entry.data)

        # todo
        except Exception as e:
            logging.error("_waiting_loop error: %s" % e)


class RateLimiter(object):

    def when(self, item) -> int:
        pass

    def forget(self, item):
        pass

    def num_requeues(self, item) -> int:
        pass


# todo
class SimpleRateLimiter(RateLimiter):
    def when(self, item) -> int:
        return 5

    def forget(self, item):
        pass

    def num_requeues(self, item) -> int:
        return 0


def default_rate_limiter():
    return SimpleRateLimiter()


class RateLimitingInterface(DelayingType):

    def add_rate_limited(self, item):
        pass

    def forget(self, item):
        pass

    def num_requeues(self, itme) -> int:
        pass


class RateLimitingType(RateLimitingInterface):

    def __init__(self, rate_limiter: RateLimiter=None):
        super(RateLimitingType, self).__init__()
        if not rate_limiter:
            rate_limiter = default_rate_limiter()
        self.rate_limiter = rate_limiter

    def add_rate_limited(self, item):
        self.add_after(item, self.rate_limiter.when(item))

    def forget(self, item):
        self.rate_limiter.forget(item)

    def num_requeues(self, itme) -> int:
        return self.rate_limiter.num_requeues(itme)
