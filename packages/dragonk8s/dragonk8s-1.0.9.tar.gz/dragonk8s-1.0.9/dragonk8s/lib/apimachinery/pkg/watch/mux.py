from threading import Lock, Event
from queue import Queue, Full, Empty
from dragonk8s.lib.apimachinery.pkg.watch.watch import Interface, Event as MyEvent
from dragonk8s.lib.pool.thread_manager import GlobalThreadManager

internalRunFunctionMarker = "internal-do-function"


class FullQueueBehavior(object):
    WaitIfChannelFull = 0
    DropIfChannelFull = 1


class Broadcaster(object):

    def __init__(self, queue_length: int, full_queue_behavior: int):
        self._watchers = {}
        self._next_watcher = 0
        self._incoming = Queue(25)
        self._watch_queue_length = queue_length
        self._full_queue_behavior = full_queue_behavior
        self._distributing = Event()
        self._stopped = False
        backend = GlobalThreadManager.new_thread(target=self._loop, generate_name="Broadcaster start", daemon=True)
        backend.start()

    def _block_queue(self, f):
        if self._stopped:
            return
        event = Event()

        def fake_obj():
            event.set()
            f()

        self._incoming.put(MyEvent(_type=internalRunFunctionMarker, obj=fake_obj))
        event.wait()

    def watch(self) -> Interface:
        watcher = BroadcasterWatcher()

        def f():
            cur_id = self._next_watcher
            self._next_watcher += 1
            watcher.id = cur_id
            watcher.m = self
            watcher.result = Queue(self._watch_queue_length)
            self._watchers[cur_id] = watcher

        self._block_queue(f)
        if watcher.m is None:
            raise Exception("broadcaster already stopped")
        return watcher

    def watch_with_prefix(self, queued_events) -> Interface:
        watcher = BroadcasterWatcher()

        def f():
            cur_id = self._next_watcher
            self._next_watcher += 1
            length = self._watch_queue_length
            n = len(queued_events) + 1
            if n > length:
                length = n
            watcher.id = cur_id
            watcher.m = self
            watcher.result = Queue(length)
            self._watchers[cur_id] = watcher
            for queued_event in queued_events:
                watcher.result.put(queued_event)
        self._block_queue(f)
        if watcher.m is None:
            raise Exception("broadcaster already stopped")
        return watcher

    def stop_watching(self, _id: int):

        def f():
            if _id in self._watchers.keys():
                del self._watchers[_id]
        self._block_queue(f)

    def _close_all(self):
        self._watchers.clear()

    def action(self, action: str, obj):
        if not self._stopped:
            try:
                self._incoming.put(MyEvent(action, obj), block=True, timeout=5)
            except Full:
                return

    def action_or_drop(self, action: str, obj) -> bool:
        try:
            self._incoming.put(MyEvent(action, obj), block=False)
            return True
        except Full:
            return False

    def shutdown(self):

        def f():
            self._stopped = True
        self._block_queue(f)
        self._distributing.wait()

    def _loop(self):
        while not self._stopped:
            try:
                event = self._incoming.get(block=True, timeout=5)
                if event.type == internalRunFunctionMarker:
                    event.obj()
                    continue
                self._distribute(event)
            except Empty:
                continue
        self._close_all()
        self._distributing.set()

    def _distribute(self, event):
        if self._full_queue_behavior == FullQueueBehavior.DropIfChannelFull:
            for w in self._watchers.values():
                if not w.stopped:
                    try:
                        w.result.put(event, block=False)
                    except Full:
                        break
        else:
            for w in self._watchers.values():
                while not w.stopped:
                    try:
                        w.result.put(event, block=True, timeout=5)
                        break
                    except Full:
                        continue


class BroadcasterWatcher(Interface):

    def __init__(self, _id=0, result_queue: Queue = None, m: Broadcaster = None):
        self.result = result_queue
        self.stopped = False
        self._stop_lock = Lock()
        self.id = _id
        self.m = m

    def stop(self):
        if self.stopped:
            return
        if not self._stop_lock.acquire():
            return
        try:
            if self.stopped:
                return
            self.stopped = True
            self.m.stop_watching(self.id)
        finally:
            self._stop_lock.release()

    def get_result_queue(self) -> Queue:
        return self.result
