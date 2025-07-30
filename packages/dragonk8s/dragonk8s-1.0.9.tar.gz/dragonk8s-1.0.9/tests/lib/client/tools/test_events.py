import time
import unittest
import logging
from threading import Event
from kubernetes import config
from dragonk8s.lib.client.tools import events
from kubernetes.client.models.v1_pod import V1Pod
from kubernetes.client.models.v1_object_meta import V1ObjectMeta
from dragonk8s.lib.client.kubernetes.typed.core.v1.event_expansion import EventSinkImpl
from dragonk8s.dragon.configuration import Configuration
from dragonk8s.lib.client import CommonClient
from dragonk8s.dragon.api_client import ApiClient


class EventsTest(unittest.TestCase):

    def setUp(self):
        cfg = Configuration()
        config.load_kube_config(config_file="C:\\Users\\Administrator\\.kube\\config", client_configuration=cfg)
        Configuration.set_default(cfg)
        self.base_client = ApiClient()
        client = CommonClient(self.base_client)

        sink = events.EventSinkImpl(client)
        self.event_broadcaster = events.EventBroadcasterImpl(sink=sink)
        self.event_recorder = self.event_broadcaster.new_recorder("mhc-controller")
        self.stop = Event()
        print(self.stop.is_set())
        self.event_broadcaster.start_recording_to_sink(self.stop)
        self.event_broadcaster.start_structured_logging(self.stop)

    def test1(self):
        pod = V1Pod(
            kind="Pod",
            api_version="v1",
            metadata=V1ObjectMeta(
                name="bbb",
                namespace="default"
            ),
        )
        self.event_recorder.eventf(pod, None, events.EventTypeNormal, "MHCReason", "mhc-action", "some message....")
        time.sleep(5)

    def test2(self):
        pod = V1Pod(
            kind="Pod",
            api_version="v1",
            metadata=V1ObjectMeta(
                name="bbb",
                namespace="default"
            ),
        )
        for i in range(5):
            self.event_recorder.eventf(pod, None, events.EventTypeNormal, "MHCReason", "mhc-action", "some message....")
            time.sleep(1)
        time.sleep(90)

    def tearDown(self) -> None:
        print("shut down")
        self.stop.set()
        self.event_broadcaster.shut_down()
