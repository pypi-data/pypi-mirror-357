import time
import unittest
from kubernetes import config
from dragonk8s.lib.client.tools import record
from kubernetes.client.models.v1_event_source import V1EventSource
from kubernetes.client.models.v1_pod import V1Pod
from kubernetes.client.models.v1_object_meta import V1ObjectMeta
from dragonk8s.lib.client.kubernetes.typed.core.v1.event_expansion import EventSinkImpl


class EventSinkImplTest(unittest.TestCase):

    def setUp(self):
        config.load_kube_config(config_file="/Users/bytedance/.kube/config")
        self.event_broadcaster = record.EventBroadcasterImpl()
        source = V1EventSource(component="mhc", host="1.2.3.4")
        self.event_recorder = self.event_broadcaster.new_recorder(source)
        self.event_broadcaster.start_recording_to_sink(EventSinkImpl())
        self.event_broadcaster.start_structured_logging()

    def test1(self):
        pod = V1Pod(
            kind="Pod",
            api_version="v1",
            metadata=V1ObjectMeta(
                name="bbb",
                namespace="kube-system"
            ),
        )
        self.event_recorder.event(pod, record.EventTypeNormal, "MHCReason", "some message....")
        time.sleep(5)

    def tearDown(self) -> None:
        print("shut down")
        self.event_broadcaster.shut_down()
