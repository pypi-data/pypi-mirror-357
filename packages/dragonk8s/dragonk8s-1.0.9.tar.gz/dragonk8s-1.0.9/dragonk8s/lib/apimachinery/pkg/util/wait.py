import threading
import time
import logging
from dragonk8s.lib.pool.thread_manager import GlobalThreadManager
from threading import Event


def until(f, period: int, stop_event: Event):
    count = 0
    while not stop_event.is_set():
        if count == period:
            f()
            count = 0
        else:
            count += 1
            time.sleep(1)


def until_named(f, period: int, stop_event: Event, name):
    count = 0
    while not stop_event.is_set():
        if count == period:
            f()
            count = 0
        else:
            count += 1
            time.sleep(1)
    logging.info("stop until %s" % name)


def until_with_thread(f, period: int, stop_event: Event, name):
    def do(df, dperiod, dstop_event):
        until_named(df, dperiod, dstop_event, name)
    backend = GlobalThreadManager.new_thread(generate_name="until_with_thread_%s" % name, target=do, args=(f, period, stop_event))
    backend.start()


class TimeOutException(Exception):
    pass


def poll(f, period: int, timeout: int, stop: threading.Event, immadiate=False) -> bool:
    if timeout < 1:
        timeout = 0
    t = 0
    ok = False
    while not stop.is_set():
        if immadiate:
            ok = f()
        if t % period == 0:
            ok = f()
        if ok:
            return True
        time.sleep(1)
        t += 1
        if 0 < timeout < t:
            return False
    logging.info("stop poll %s" % f.__name__)
    return False
