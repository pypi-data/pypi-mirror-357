import datetime
import socket
import time

import copy
import json
import logging
from threading import Event, Lock, Thread
from kubernetes.client.api.events_v1_api import EventsV1Api
from kubernetes.client.models.events_v1_event import EventsV1Event
from dragonk8s.lib.apimachinery.pkg.watch import watch, mux
from kubernetes.client.exceptions import ApiException
from kubernetes.client.models.events_v1_event_series import EventsV1EventSeries
from dragonk8s.lib.apimachinery.pkg.util import wait
from dragonk8s.lib.client.tools import reference
from kubernetes.client.models.v1_object_reference import V1ObjectReference
from dragonk8s.lib.apimachinery.pkg.apis import meta_v1
from kubernetes.client.models.v1_object_meta import V1ObjectMeta
from dragonk8s.lib.util import timeutil
from dragonk8s.lib.apimeta import apigvk
from dragonk8s.lib.apimachinery.pkg.types import patch
from dragonk8s.lib.pool.thread_manager import GlobalThreadManager


finishTime = 1 * 60
refreshTime = 30

EventTypeNormal = "Normal"
EventTypeWarning = "Warning"


def get_event_string(event: EventsV1Event, indent=4) -> str:
    res = {}
    for k, v in event.to_dict().items():
        if k.startswith("deprecated_"):
            continue
        if k == "managedFields":
            continue
        res[k] = v
    return json.dumps(res, indent=indent)


def validate_event_type(eventtype: str) -> bool:
    if eventtype == EventTypeNormal or eventtype == EventTypeWarning:
        return True
    return False


def is_key_not_found_error(ex) -> bool:
    return ex is not None and ex.status == 404


class EventRecorder(object):

    def eventf(self, regarding, related, eventtype: str, reason: str, action: str, note: str, *args):
        pass


class EventBroadcaster(object):

    def start_recording_to_sink(self, stop_event: Event):
        pass

    def new_recorder(self, reporting_controller: str) -> EventRecorder:
        pass

    def start_event_watcher(self, event_handler, stop_event: Event):
        pass

    def start_structured_logging(self, stop_event: Event):
        pass

    def shut_down(self):
        pass


class EventSink(object):

    def create(self, event: EventsV1Event) -> EventsV1Event:
        return EventsV1Event()

    def update(self, event: EventsV1Event) -> EventsV1Event:
        return EventsV1Event()

    def patch(self, event: EventsV1Event, data) -> EventsV1Event:
        return EventsV1Event()


def ref_2_str(ref):
    if ref is None:
        return ""
    if isinstance(ref, V1ObjectReference):
        ref = ref.to_dict()
    return json.dumps(ref)


class EventKey(object):

    def __init__(self, action: str = "", reason: str = "", reporting_controller: str = "", regarding=None,
                 related=None):
        self.action = action
        self.reason = reason,
        self.reporting_controller = reporting_controller
        self.regarding = regarding
        self.related = related

    def __str__(self):
        return "action={},reason={},reporting_controller={},regarding={},related={}".format(
            self.action, self.reason, self.reporting_controller, ref_2_str(self.regarding), ref_2_str(self.related))

    def __repr__(self):
        return self.__str__()


def _get_key(event: EventsV1Event) -> EventKey:
    key = EventKey(
        action=event.action,
        reason=event.reason,
        reporting_controller=event.reporting_controller,
        regarding=event.regarding,
    )
    if event.related is not None:
        key.related = event.related
    return str(key)


class EventSinkImpl(EventSink):

    def __init__(self, kube_client):
        super().__init__()
        self.client = apigvk.get_resource_client(kube_client, apigvk.EventsV1Event)

    def create(self, event: EventsV1Event) -> EventsV1Event:
        if event.metadata is None or event.metadata.namespace == "":
            raise Exception("can't create an event with empty namespace")
        return self.client.create(event)

    def update(self, event: EventsV1Event) -> EventsV1Event:
        if event.metadata is None or event.metadata.namespace == "":
            raise Exception("can't update an event with empty namespace")
        return self.client.replace(body=event, name=event.metadata.name, namespace=event.metadata.namespace)

    def patch(self, event: EventsV1Event, data) -> EventsV1Event:
        if event.metadata is None or event.metadata.namespace == "":
            raise Exception("can't patch an event with empty namespace")
        return self.client.patch(body=data, name=event.metadata.name,
                                                  namespace=event.metadata.namespace,
                                                  content_type=patch.PatchType.StrategicMergePatchType)


def _create_patch_for_series(event: EventsV1Event) -> dict:
    if event.series is None:
        return dict()
    return dict(
        series=dict(
            count=event.series.count,
            lastObservedTime=timeutil.to_time_str_with_ns(event.series.last_observed_time),
        )
    )


def _record_event(sink: EventSink, event: EventsV1Event) -> (EventsV1Event, bool):
    new_event = None
    ex = None
    is_event_series = event.series is not None
    if is_event_series:
        patch = _create_patch_for_series(event)
        try:
            new_event = sink.patch(event, patch)
        except ApiException as e:
            ex = e
    if not is_event_series or (is_event_series and is_key_not_found_error(ex)):
        ex = None
        event.metadata.resource_version = ""
        try:
            new_event = sink.create(event)
        except ApiException as e:
            ex = e
    if ex is None:
        return new_event, False
    logging.error("Unable to write event: %s, err: %s (may retry after sleeping)" % (event.metadata.name, str(ex)))
    return None, True


class RecorderImpl(EventRecorder):

    def __init__(self, reporting_controller: str = "", reporting_instance: str = "", broadcaster:mux.Broadcaster = None):
        self.reporting_controller = reporting_controller
        self.reporting_instance = reporting_instance
        self.broadcaster = broadcaster

    def _make_event(self, ref_regarding: V1ObjectReference, refRelated: V1ObjectReference, timestamp: float, eventtype,
                    reason, message, reporting_controller, reporting_instance, action) -> EventsV1Event:
        namespace = ref_regarding.namespace
        if namespace is None or namespace == "":
            namespace = meta_v1.NamespaceDefault
        return EventsV1Event(
            api_version="events.k8s.io/v1",
            kind="Event",
            metadata=V1ObjectMeta(
                name="%s.%f" % (ref_regarding.name, timestamp),
                namespace=namespace,
            ),
            event_time=timeutil.to_time_str_with_ns(timestamp),
            series=None,
            reporting_controller=reporting_controller,
            reporting_instance=reporting_instance,
            action=action,
            reason=reason,
            regarding=ref_regarding,
            related=refRelated,
            note=message,
            type=eventtype,
        )

    def eventf(self, regarding, related, eventtype: str, reason: str, action: str, note: str, *args):
        timestamp = time.time()
        message = note.format(*args)
        try:
            ref_regarding = reference.get_reference(regarding)
        except Exception as e:
            logging.error("Could not construct reference to %s due to %s, will not report event: '%s' '%s' '%s'"
                          % (str(ref_regarding), str(e), eventtype, reason, message))
            return
        ref_related = None
        if related is not None:
            try:
                ref_related = reference.get_reference(related)
            except Exception as e:
                logging.error("Could not construct reference to %s due to %s, will not report event: '%s' '%s' '%s'"
                              % (str(related), str(e), eventtype, reason, message))
        if not validate_event_type(eventtype):
            logging.error("Unsupported event type: %s" % eventtype)
            return

        event = self._make_event(ref_regarding, ref_related, timestamp, eventtype, reason, message,
                                 self.reporting_controller, self.reporting_instance, action)
        # todo: 异步
        self.broadcaster.action(watch.EventType.Added, event)


class EventBroadcasterImpl(EventBroadcaster):

    def __init__(self, sink: EventSink):
        self.broadcaster = mux.Broadcaster(1000, mux.FullQueueBehavior.DropIfChannelFull)
        self.lock = Lock()
        self.event_cache = dict()
        self.sleep_duration = 10
        self.sink = sink

    def start_recording_event(self, stop_event: Event):
        def handle(obj):
            self.record_to_sink(event=obj)
        stop_watcher = self.start_event_watcher(handle, stop_event)

        # def wait_stop():
        #     while stop_event.wait(10):
        #         pass
        #     print("stop watcher...")
        #     stop_watcher()
        # backend = Thread(target=wait_stop, name="wait_stop")
        # backend.start()

    def start_recording_to_sink(self, stop_event: Event):
        wait.until_with_thread(self._refresh_existing_event_series, refreshTime, stop_event, "_refresh_existing_event_series")
        wait.until_with_thread(self._finish_series, finishTime, stop_event, "_finish_series")
        self.start_recording_event(stop_event)

    def new_recorder(self, reporting_controller: str) -> EventRecorder:
        hostname = socket.gethostname()
        reporting_instance = "{}-{}".format(reporting_controller, hostname)
        return RecorderImpl(
            reporting_controller=reporting_controller,
            reporting_instance=reporting_instance,
            broadcaster=self.broadcaster,
        )

    def start_event_watcher(self, event_handler, stop_event: Event):
        watcher = self.broadcaster.watch()

        def do():
            watch_event = None
            while not stop_event.is_set():
                try:
                    watch_event = None
                    watch_event = watcher.get_result_queue().get(True, 5)
                except:
                    time.sleep(1)
                if watch_event is None:
                    continue
                event_handler(watch_event.obj)
        backend = GlobalThreadManager.new_thread(target=do, generate_name="start_event_watcher")
        backend.start()
        return watcher.stop

    def start_structured_logging(self, stop_event: Event):
        def do(obj: EventsV1Event):
            logging.info(get_event_string(obj))
        self.start_event_watcher(do, stop_event)

    def shut_down(self):
        self.broadcaster.shutdown()

    def _refresh_existing_event_series(self):
        try:
            self.lock.acquire(True)
            for k, event in self.event_cache.items():
                if event.series is not None:
                    recorded_event, retry = _record_event(self.sink, event)
                    if not retry and recorded_event is not None:
                        self.event_cache[k] = recorded_event
        finally:
            self.lock.release()

    def _finish_series(self):
        now = time.time()
        with self.lock:
            to_delete = []
            for k, event in self.event_cache.items():
                event_serie = event.series
                if event_serie is not None:
                    if event_serie.last_observed_time.timestamp() < now - finishTime:
                        recorded_event, retry = _record_event(self.sink, event)
                        if not retry:
                            to_delete.append(k)
                else:
                    if isinstance(event.event_time, str):
                        logging.error("event time is str: %s" % event.event_time)
                        to_delete.append(k)
                    else:
                        if event.event_time.timestamp() < now - finishTime:
                            to_delete.append(k)
            for k in to_delete:
                del self.event_cache[k]

    def _attempt_recording(self, event: EventsV1Event) -> EventsV1Event:
        tries = 0
        while True:
            recorded_event, retry = _record_event(self.sink, event)
            if not retry:
                return recorded_event
            tries += 1
            if tries >= 12:
                logging.error("unable to write event: %s (retry limit exceeded)" % event.metadata.name)
                return None
            time.sleep(self.sleep_duration)

    # todo: 并行
    def record_to_sink(self, event: EventsV1Event):
        event_copy = copy.deepcopy(event)

        def do() -> EventsV1Event:
            try:
                self.lock.acquire(True)
                event_key = _get_key(event_copy)
                if event_key in self.event_cache:
                    event_in_cache = self.event_cache[event_key]
                    if event_in_cache.series is not None:
                        event_in_cache.series.count += 1
                        event_in_cache.series.last_observed_time = datetime.datetime.now()
                        return None
                    event_in_cache.series = EventsV1EventSeries(
                        count=2,
                        last_observed_time=datetime.datetime.now(),
                    )
                    return event_in_cache
                self.event_cache[event_key] = event_copy
                return event_copy
            finally:
                self.lock.release()
        ev_to_record = do()
        if ev_to_record is not None:
            recorded_event = self._attempt_recording(ev_to_record)
            if recorded_event is not None:
                recorded_event_key = _get_key(recorded_event)
                try:
                    self.lock.acquire(True)
                    self.event_cache[recorded_event_key] = recorded_event
                finally:
                    self.lock.release()
