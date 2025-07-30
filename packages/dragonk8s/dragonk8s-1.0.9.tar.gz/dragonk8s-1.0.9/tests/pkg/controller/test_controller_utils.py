import time
import unittest
from kubernetes import config
from threading import Event
from kubernetes.client.models.v1_object_meta import V1ObjectMeta
from dragonk8s.pkg.controller.controller_utils import RealPodControl
from dragonk8s.lib.client.tools import events
from kubernetes.client.models.v1_replica_set import V1ReplicaSet
from kubernetes.client.models.v1_pod_template_spec import V1PodTemplateSpec
from kubernetes.client.models.v1_pod_spec import V1PodSpec
from kubernetes.client.models.v1_container import V1Container
from kubernetes.client.models.v1_owner_reference import V1OwnerReference
from dragonk8s.dragon.api_client import ApiClient
from dragonk8s.lib.client import CommonClient
from dragonk8s.lib.apimeta import apigvk
from dragonk8s.dragon.configuration import Configuration


class RealPodControlTest(unittest.TestCase):

    def setUp(self):
        cfg = Configuration()
        config.load_kube_config(config_file="C:\\Users\\Administrator\\.kube\\config", client_configuration=cfg)
        Configuration.set_default(cfg)
        self.base_client = ApiClient()

        client = CommonClient(self.base_client)
        sink = events.EventSinkImpl(client)
        self.event_broadcaster = events.EventBroadcasterImpl(sink=sink)
        self.event_recorder = self.event_broadcaster.new_recorder("mhc-controller")
        self.pod_control = RealPodControl(client, self.event_recorder)
        self.controller = V1ReplicaSet(
            kind="ReplicaSet",
            api_version="v1",
            metadata=V1ObjectMeta(
                name="mhc-replica",
                namespace="default",
            ),
        )
        self.controller_ref = V1OwnerReference(
            name="mhc-replica",
            kind="ReplicaSet",
            api_version="v1",
            uid="123",
            controller=True,
            block_owner_deletion=True,

        )
        self.stop = Event()
        self.event_broadcaster.start_recording_to_sink(self.stop)
        self.event_broadcaster.start_structured_logging(self.stop)

    def test_create(self):
        ns = "default"
        container = V1Container(
            name="test",
            image="registry.cn-beijing.aliyuncs.com/mhc_base/linux-tools:net",
            command=["tail", "-f", "/dev/null"]
        )
        template = V1PodTemplateSpec(
            metadata=V1ObjectMeta(
                labels={"app": "test"}
            ),
            spec=V1PodSpec(
                containers=[container]
            )
        )
        self.pod_control.create_pod(ns, template, self.controller, self.controller_ref)

    def test_get(self):
        pod = self.pod_control.kube_client.get(namespace="default", name="mhc-replica-4rh58")
        print(pod.status.start_time.timestamp())

    def test_delete(self):
        self.pod_control.delete_pod("default", "mhc-replica-qsprs", self.controller)

    def test_patch(self):
        data = {
            "metadata": {
                "labels": {"app": "test", "aa2": "bb2"}
            }
        }
        self.pod_control.patch_pod("default", "mhc-replica-fhbmj", data)

    def test_patch2(self):
        data = {
            "metadata": {
                "uid": "",
                "ownerReferences": [
                    {
                        "apiVersion": "v1",
                        "kind": "ReplicaSet",
                        "name": "mmm2",
                        "uid": "222",
                        "controller": False,
                        "blockOwnerDeletion": True
                    }
                ],
                "finalizers": []
            }
        }
        self.pod_control.patch_pod("default", "mhc-replica-fhbmj", data)

    def tearDown(self) -> None:
        print("shut down")
        time.sleep(3)
        self.stop.set()
        self.event_broadcaster.shut_down()
