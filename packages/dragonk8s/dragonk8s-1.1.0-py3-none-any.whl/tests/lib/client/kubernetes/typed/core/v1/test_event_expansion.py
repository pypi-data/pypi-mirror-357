import time
import unittest
from kubernetes import config
from kubernetes.client.models.core_v1_event import CoreV1Event
from kubernetes.client.models.v1_object_meta import V1ObjectMeta
from kubernetes.client.models.v1_object_reference import V1ObjectReference
from dragonk8s.lib.client.kubernetes.typed.core.v1.event_expansion import EventSinkImpl
from kubernetes.client.exceptions import ApiException
from dragonk8s.lib.apimachinery.pkg.api import errors
import datetime
from kubernetes.client.models.v1_status import V1Status
from dragonk8s.lib.client.util.trans import parse_v1_status, parse_json_to_object, parse_json_to_object_by_class_name


class EventSinkImplTest(unittest.TestCase):

    def setUp(self):
        config.load_kube_config(config_file="/Users/bytedance/.kube/config")
        self.event_sink = EventSinkImpl()

    def test_create_event(self):
        event = CoreV1Event(
            api_version="v1",
            kind="Event",
            metadata=V1ObjectMeta(
                name="m13",
                namespace="kube-system"
            ),
            # event_time="2022-11-30T02:21:25.458481Z",
            action="Action11",
            type="Normal",
            reason="somereason",
            message="some message",
            involved_object=V1ObjectReference(
                api_version="v1",
                kind="Pod",
                name="coredns-7f74c56694-qsrts",
                namespace='kube-system'
            ),
            reporting_component="default-scheduler11",
            reporting_instance="default-scheduler-vm10-0-11-1211111",
            count=2,
        )
        try:
            self.event_sink.create(event)
        except ApiException as e:
            print(e.status)
            print(e.reason)
            # status = parse_v1_status(e.body)
            # status = parse_json_to_object(e.body, V1Status())
            status = parse_json_to_object_by_class_name(e.body, "V1Status")
            print(status.to_dict())
            print(status.api_version)
            print(status.code)
            print(status.reason)
            print(status.details)
            raise e

    def test_create_event_exist(self):
        event = CoreV1Event(
            api_version="v1",
            kind="Event",
            metadata=V1ObjectMeta(
                name="m12",
                namespace="kube-system"
            ),
            event_time="2022-11-30T02:21:25.458481Z",
            action="Action11",
            type="Normal",
            reason="somereason",
            message="some message",
            involved_object=V1ObjectReference(
                api_version="v1",
                kind="Pod",
                name="coredns-7f74c56694-qsrts",
                namespace='kube-system'
            ),
            reporting_component="default-scheduler11",
            reporting_instance="default-scheduler-vm10-0-11-1211111",
            count=2,
            first_timestamp="2022-11-30T02:21:25.458481Z",
        )
        try:
            self.event_sink.create(event)
        except ApiException as e:
            if errors.is_already_exists(e):
                print("is exist")
            else:
                raise e

    def test_update_event(self):
        event = CoreV1Event(
            api_version="v1",
            kind="Event",
            metadata=V1ObjectMeta(
                name="m1",
                namespace="kube-system"
            ),
            event_time="2022-11-30T02:21:25.458481Z",
            action="Action11",
            type="Normal",
            reason="somereason111",
            message="some message",
            involved_object=V1ObjectReference(
                api_version="v1",
                kind="Pod",
                name="coredns-7f74c56694-qsrts",
                namespace='kube-system'
            ),
            reporting_component="default-scheduler11",
            reporting_instance="default-scheduler-vm10-0-11-1211111"
        )
        self.event_sink.update(event)

    def test_patch_event(self):
        event = self.event_sink.client.read_namespaced_event("m12", "kube-system")
        print(event.to_dict())
        tot = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(tot)
        data = {
            "reportingComponent": "wahah222",
            "lastTimestamp": datetime.datetime.now(),
            "count": 22,
        }
        event = self.event_sink.patch(event, data)
        print(event.to_dict())

    def test_not_found(self):
        try:
            event = self.event_sink.client.read_namespaced_event("m2222", "kube-system")
            print(event.to_dict())
        except ApiException as e:
            print(e.status)

    def test_get(self):
        try:
            event = self.event_sink.client.read_namespaced_event("m12", "kube-system")
            print(event.to_dict())
            print(event.first_timestamp.timestamp())
            print(datetime.datetime.fromtimestamp(time.time()))
        except ApiException as e:
            print(e.status)