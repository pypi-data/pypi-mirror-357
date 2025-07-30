import threading
import traceback
import json
from queue import Empty
import logging
import time
from kubernetes.client.models.v1_object_meta import V1ObjectMeta
from kubernetes.client.models.v1_event_source import V1EventSource
from kubernetes.client.models.v1_object_reference import V1ObjectReference
from dragonk8s.lib.apimachinery.pkg.watch import watch, mux
from kubernetes.client.models.core_v1_event import CoreV1Event
from kubernetes.client.exceptions import ApiException
from dragonk8s.lib.apimachinery.pkg.api import errors
from copy import deepcopy
from threading import RLock
from dragonk8s.lib.util.cache import lru
from dragonk8s.lib.client.util.flow_control import TokenBucketRateLimiter
from dragonk8s.lib.util import timeutil
from dragonk8s.lib.apimachinery.pkg.apis import meta_v1
from dragonk8s.lib.client.tools import reference
from dragonk8s.lib.pool.thread_manager import GlobalThreadManager


EventTypeNormal = "Normal"
EventTypeWarning = "Warning"


def validate_event_type(eventtype: str) -> bool:
    if eventtype == EventTypeNormal or eventtype == EventTypeWarning:
        return True
    return False


class RecordException(Exception):
    pass


def is_key_not_found_error(ex) -> bool:
    return ex is not None and ex.status == 404


def event_aggregator_by_reason_func(event: CoreV1Event) -> (str, str):
    ss = [event.source.component, event.source.host, event.involved_object.kind, event.involved_object.namespace,
          event.involved_object.name, event.involved_object.uid, event.involved_object.api_version,
          event.type, event.reason, event.reporting_component, event.reporting_instance]
    tos = [str(s) for s in ss]
    return "".join(tos), event.message


def event_aggregator_by_reason_message_func(event: CoreV1Event) -> str:
    return "(combined from similar events): %s" % event.message


def get_spam_key(event: CoreV1Event) -> str:
    ss = [event.source.component, event.source.host, event.involved_object.kind, event.involved_object.namespace,
          event.involved_object.name, event.involved_object.uid, event.involved_object.api_version]
    tos = [str(s) for s in ss]
    return "".join(tos)


def get_event_key(event: CoreV1Event) -> str:
    ss = [event.source.component, event.source.host, event.involved_object.kind, event.involved_object.namespace,
          event.involved_object.name, event.involved_object.field_path, event.involved_object.uid,
          event.involved_object.api_version, event.type, event.reason, event.message]
    tos = [str(s) for s in ss]
    return "".join(tos)


class EventSink(object):

    def create(self, event: CoreV1Event) -> CoreV1Event:
        return CoreV1Event()

    def update(self, event: CoreV1Event) -> CoreV1Event:
        return CoreV1Event()

    def patch(self, old_event: CoreV1Event, data) -> CoreV1Event:
        return CoreV1Event()


class EventRecorder(object):

    def event(self, obj, event_type: str, reason: str, message: str):
        pass

    def eventf(self, obj, eventtype: str, reason: str, message_fmt: str, *args):
        pass

    def annotated_eventf(self, obj, annotations: dict, eventtype: str, reason: str, message_fmt: str, *args):
        pass


class EventBroadcaster(object):

    def start_event_watcher(self, event_handler) -> watch.Interface:
        pass

    def start_recording_to_sink(self, sink: EventSink) -> watch.Interface:
        pass

    def start_logging(self, logf) -> watch.Interface:
        pass

    def start_structured_logging(self, level) -> watch.Interface:
        pass

    def new_recorder(self, scheme, source: V1EventSource) -> EventRecorder:
        pass

    def shut_down(self):
        pass


class SpamRecord(object):

    def __init__(self, rate_limiter: TokenBucketRateLimiter = None):
        self.rate_limiter = rate_limiter


class EventSourceObjectSpamFilter(object):

    def __init__(self, lru_cache_size: int, burst: int, qps: float, spam_key_func):
        self._lock = RLock()
        self._cache = lru.Cache(lru_cache_size)
        self._burst = burst
        self._qps = qps
        self._spam_key_func = spam_key_func

    def filter(self, event: CoreV1Event):
        record = SpamRecord()
        event_key = self._spam_key_func(event)
        try:
            self._lock.acquire()
            value, found = self._cache.get(event_key)
            if found:
                record = value
            if record.rate_limiter is None:
                record.rate_limiter = TokenBucketRateLimiter(self._qps, self._burst)
            fil = not record.rate_limiter.try_accept()
            self._cache.add(event_key, record)
            return fil
        finally:
            self._lock.release()


class AggregateRecord(object):

    def __init__(self, local_keys=None, last_timestamp=0):
        if local_keys is None:
            self.local_keys = []
        else:
            self.local_keys = local_keys
        self.last_timestamp = last_timestamp


class EventAggregator(object):

    def __init__(self, lru_cache_size, key_func, message_func, max_events, max_interval_in_seconds):
        self._lock = RLock()
        self._cache = lru.Cache(lru_cache_size)
        self._key_func = key_func
        self._message_func = message_func
        self._max_events = max_events
        self._max_interval_in_seconds = max_interval_in_seconds

    def event_aggregate(self, new_event: CoreV1Event) -> (CoreV1Event, str):
        now = time.time()
        record = AggregateRecord()
        event_key = get_event_key(new_event)
        aggregate_key, local_key = self._key_func(new_event)

        try:
            self._lock.acquire(True)
            value, found = self._cache.get(aggregate_key)
            if found:
                record = value

            max_interval = self._max_interval_in_seconds
            interval = now - record.last_timestamp
            if interval > max_interval:
                record = AggregateRecord(local_keys=[])

            record.local_keys.append(local_key)
            record.last_timestamp = now
            self._cache.add(aggregate_key, record)

            if len(record.local_keys) < self._max_events:
                return new_event, event_key

            record.local_keys.pop()
            event = CoreV1Event(
                api_version="v1",
                kind="Event",
                metadata=V1ObjectMeta(
                    name="%s.%d" % (new_event.involved_object.name, now),
                    namespace=new_event.metadata.namespace
                ),
                count=1,
                first_timestamp=timeutil.to_time_str(now),
                involved_object=new_event.involved_object,
                last_timestamp=timeutil.to_time_str(now),
                message=self._message_func(new_event),
                type=new_event.type,
                reason=new_event.reason,
                source=new_event.source,
            )
            return event, aggregate_key
        finally:
            self._lock.release()


class EventLog(object):

    def __init__(self, count: int = 0, first_timestamp: float=0, name="", resource_version=""):
        self.count = count
        self.first_timestamp = first_timestamp
        self.name = name
        self.resource_version = resource_version


class EventLogger(object):

    def __init__(self, lru_cache_entries: int):
        self._lock = RLock()
        self._cache = lru.Cache(lru_cache_entries)

    def event_observe(self, new_event: CoreV1Event, key: str) -> (CoreV1Event, str):
        event = deepcopy(new_event)
        patch = {}
        try:
            self._lock.acquire(True)
            last_observation = self._last_event_observation_from_cache(key)
            if last_observation.count > 0:
                event.name = last_observation.name
                event.metadata.resource_version = last_observation.resource_version
                event.first_timestamp = timeutil.to_time_str(last_observation.first_timestamp)
                event.count = last_observation.count + 1

                patch = dict(
                    count=event.count,
                    lastTimestamp=timeutil.to_time_str(event.last_timestamp),
                    message=event.message
                )
            self._cache.add(key, EventLog(count=event.count,
                                          first_timestamp=timeutil.parse_time(event.first_timestamp),
                                          name=event.metadata.name,
                                          resource_version=event.metadata.resource_version))
            return event, patch

        finally:
            self._lock.release()

    def _last_event_observation_from_cache(self, key) -> EventLog:
        value, ok = self._cache.get(key)
        if ok:
            return value
        return EventLog()

    def update_state(self, event: CoreV1Event):
        key = get_event_key(event)
        try:
            self._lock.acquire(True)
            self._cache.add(key, EventLog(count=event.count,
                                          first_timestamp=timeutil.parse_time(event.first_timestamp),
                                          name=event.metadata.name,
                                          resource_version=event.metadata.resource_version))
        finally:
            self._lock.release()


class CorrelatorOptions(object):

    def __init__(self, lru_cache_size=4096, burst_size=25, qps=float(1./300.),
                 key_func=event_aggregator_by_reason_func,
                 message_func=event_aggregator_by_reason_message_func,
                 max_events=10, max_interval_in_seconds=600, clock=None,
                 spam_key_func=get_spam_key):
        self.lru_cache_size = lru_cache_size
        self.BurstSize = burst_size
        self.qps = qps
        self.key_func = key_func
        self.message_func = message_func
        self.max_events = max_events
        self.max_interval_in_seconds = max_interval_in_seconds
        self.clock = clock
        self.spam_key_func = spam_key_func


class EventCorrelateResult(object):

    def __init__(self, event=None, patch=None, skip=False):
        self.event = event
        self.patch = patch
        self.skip = skip


class EventCorrelator(object):

    def __init__(self):
        cache_size = 4096
        spam_filter = EventSourceObjectSpamFilter(cache_size, 25, float(1.0/300.0), get_spam_key)
        self.filter_func = spam_filter.filter
        self.aggregator = EventAggregator(cache_size,
                                          event_aggregator_by_reason_func,
                                          event_aggregator_by_reason_message_func,
                                          10,
                                          600)
        self.logger = EventLogger(cache_size)

    @classmethod
    def new_with_options(cls, options: CorrelatorOptions):
        spam_filter = EventSourceObjectSpamFilter(options.lru_cache_size,
                                                  options.BurstSize,
                                                  options.qps,
                                                  options.spam_key_func)
        res = cls()
        res.filter_func = spam_filter.filter
        res.aggregator = EventAggregator(options.lru_cache_size,
                                         options.key_func,
                                         options.message_func,
                                         options.max_events,
                                         options.max_interval_in_seconds)
        res.logger = EventLogger(options.lru_cache_size)
        return res

    def event_correlate(self, new_event: CoreV1Event) -> EventCorrelateResult:
        if new_event is None:
            raise RecordException("event is None")
        aggregate_event, c_key = self.aggregator.event_aggregate(new_event)
        observed_event, patch = self.logger.event_observe(aggregate_event, c_key)
        if self.filter_func(observed_event):
            return EventCorrelateResult(skip=True)
        return EventCorrelateResult(event=observed_event, patch=patch)

    def update_state(self, event: CoreV1Event):
        self.logger.update_state(event=event)


def _record_event(sink: EventSink, event: CoreV1Event, patch: dict,
                  update_existing_event: bool, event_correlator: EventCorrelator) -> bool:
    new_event = None
    create = False
    if update_existing_event:
        try:
            new_event = sink.patch(event, patch)
        except ApiException as e:
            if is_key_not_found_error(e):
                create = True
            else:
                logging.error("server rejected event: %s: %s (will not retry)" % (str(event), e))
                return True
        except Exception as e:
            logging.error("patch event(%s) error: %s (may retry after sleeping)" % (str(event), e))
            return False
        else:
            event_correlator.update_state(new_event)
            return True
    if not update_existing_event or create:
        event.metadata.resource_version = ''
        try:
            new_event = sink.create(event)
        except ApiException as e:
            if errors.is_already_exists(e):
                event_correlator.update_state(new_event)
                return True
            else:
                logging.error("server rejected event: %s: %s (will not retry)" % (str(event), e))
                return True
        except Exception as e:
            logging.error("patch event(%s) error: %s (may retry after sleeping)" % (str(event), e))
            return False
        else:
            event_correlator.update_state(new_event)
            return True
    return False


def _record_to_sink(sink: EventSink, event: CoreV1Event, event_correlator: EventCorrelator, sleep_duration: int):
    event_copy = deepcopy(event)
    result = None
    try:
        result = event_correlator.event_correlate(event_copy)
    except Exception as e:
        traceback.format_exc()
        logging.error("event_correlate error: %s" % e)
        return
    if result.skip:
        return
    tries = 0
    while True:
        if _record_event(sink, result.event, result.patch, result.event.count > 1, event_correlator):
            break
        tries += 1
        if tries >= 12:
            logging.error("unable to write event %s (retry limit exceeded)" % str(event_copy.__dict__))
            break
        time.sleep(sleep_duration)


class EventBroadcasterImpl(EventBroadcaster):

    def __init__(self, options: CorrelatorOptions = None, stop=threading.Event()):
        super().__init__()
        if options is None:
            options = CorrelatorOptions()
        self.watcher = mux.Broadcaster(1000, mux.FullQueueBehavior.DropIfChannelFull)
        self.sleep_duration = 10
        self.options = options
        self.stop = stop

    def start_recording_to_sink(self, sink: EventSink) -> watch.Interface:
        event_correlator = EventCorrelator.new_with_options(self.options)

        def event_handler(event: CoreV1Event):
            _record_to_sink(sink, event, event_correlator, self.sleep_duration)
        return self.start_event_watcher(event_handler)

    def shut_down(self):
        self.watcher.shutdown()

    def start_event_watcher(self, event_handler) -> watch.Interface:
        watcher = self.watcher.watch()

        def handle():
            try:
                queue = watcher.get_result_queue()
                while not self.stop.is_set():
                    try:
                        watch_event = queue.get(True, 5)
                    except Empty:
                        continue
                    else:
                        event_handler(watch_event.obj)
                    # todo
            except Exception as e:
                logging.error("handle event error: %s" % e)

        backend = GlobalThreadManager.new_thread(target=handle, generate_name="Broadcaster Loop")
        backend.start()
        return watcher

    def start_logging(self, logf) -> watch.Interface:
        def handle(e: CoreV1Event):
            logf("event(%s): type: %s, reason: %s,  %s" % (str(e.involved_object.__dict__), e.type, e.reason, e.message))
        return self.start_event_watcher(handle)

    def new_recorder(self, source: V1EventSource, scheme=None) -> EventRecorder:
        return RecorderImpl(scheme, source, self.watcher)

    def start_structured_logging(self, level=0) -> watch.Interface:
        def handle(e: CoreV1Event):
            logging.info("event: %s" % str(e.__dict__))
        return self.start_event_watcher(handle)


class RecorderImpl(EventRecorder):

    def __init__(self, scheme, source: V1EventSource, watcher: mux.Broadcaster):
        super().__init__()
        self.scheme = scheme
        self.source = source
        self.watcher = watcher

    def _make_event(self, ref: V1ObjectReference, annotations: dict, eventtype: str, reason: str, message: str) -> CoreV1Event:
        now = time.time()
        time_str = timeutil.to_time_str(now)
        namespace = ref.namespace
        if namespace == "":
            namespace = meta_v1.NamespaceDefault
        return CoreV1Event(
            api_version="v1",
            kind="Event",
            metadata=V1ObjectMeta(
                name="%s.%d" %(ref.name, now),
                namespace=namespace,
                annotations=annotations,
            ),
            involved_object=ref,
            type=eventtype,
            reason=reason,
            message=message,
            first_timestamp=time_str,
            last_timestamp=time_str,
            # event_time=time_str,
            count=1,
        )

    def _generate_event(self, obj, annotations: dict, eventtype: str, reason: str, message: str):
        try:
            ref = reference.get_reference(obj)
        except Exception as e:
            logging.error("Could not construct reference to %s due to %s, will not report event: '%s' '%s' '%s'"
                          % (str(obj), str(e), eventtype, reason, message))
            return
        if not validate_event_type(eventtype):
            logging.error("Unsupported event type: %s" % eventtype)
            return

        event = self._make_event(ref, annotations, eventtype, reason, message)
        event.source = self.source
        sent = self.watcher.action_or_drop(watch.EventType.Added, event)
        if not sent:
            logging.error("unable to record evnet: too many queued events, dropped event: %s", str(event))

    def event(self, obj, eventtype: str, reason: str, message: str):
        self._generate_event(obj, None, eventtype, reason, message)

    def eventf(self, obj, eventtype: str, reason: str, message_fmt: str, *args):
        self._generate_event(obj, None, eventtype, reason, message_fmt.format(*args))

    def annotated_eventf(self, obj, annotations: dict, eventtype: str, reason: str, message_fmt: str, *args):
        self._generate_event(obj, annotations, eventtype, reason, message_fmt.format(*args))
