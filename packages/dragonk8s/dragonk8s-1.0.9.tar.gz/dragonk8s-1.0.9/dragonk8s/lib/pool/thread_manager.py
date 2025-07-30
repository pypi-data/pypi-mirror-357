import logging
import time
import eventlet

eventlet.monkey_patch(thread=True)
from threading import Thread, Lock


class ThreadManager(object):

    def __init__(self):
        self._data = {}
        self._lock = Lock()

    def new_thread(self, target, args=(), daemon=False, generate_name=None, name="") -> Thread:
        if generate_name is not None:
            name = generate_name + str(time.time())
            while name in self._data:
                time.sleep(0.1)
                name = generate_name + str(time.time())
        if name in self._data:
            return self._data[name]
        with self._lock:
            th = Thread(target=target, args=args, name=name)
            if daemon:
                th.setDaemon(True)
            else:
                self._data[name] = th
            return th

    def join(self):
        for name, th in self._data.items():
            logging.info("wait %s..." % name)
            th.join()

    def wait_stop_and_clean(self, timeout=30) -> bool:
        count = 0
        while count <= timeout:
            to_delete = []
            have_alive = False
            for name, th in self._data.items():
                if th.is_alive():
                    # logging.debug("thread %s is already alive" % name)
                    have_alive = True
                else:
                    to_delete.append(name)
            if not have_alive:
                self._data.clear()
                break
            for n in to_delete:
                del self._data[n]
            time.sleep(1)
            count += 1
        if len(self._data) > 0:
            logging.warning("[%s] is still in running" % ", ".join(self._data.keys()))
            return False
        return True


GlobalThreadManager  = ThreadManager()

