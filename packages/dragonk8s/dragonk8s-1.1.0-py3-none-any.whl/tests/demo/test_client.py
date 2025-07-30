import datetime
import json
import queue
import threading
import unittest
from dragonk8s.lib.apimeta import apigvk
from kubernetes import config
from dragonk8s.lib.client import CommonClient
from dragonk8s.lib.client.configuration import Configuration

CoreV1Service = apigvk.GVK(
    group="", version="v1", kind="Service", response_type="V1Service")


def init_client():
    # 注册要操作的资源类型
    apigvk.register_gvk(CoreV1Service)

    # 如果想要操作自定义资源, 可以对自定义资源进行注册
    # apigvk.register_model_package("pymysqloperator.models")
    # ComDragonk8sTutorialV1PyMysql = apigvk.GVK(
    #     group="tutorial.dragonk8s.com", version="v1", kind="PyMysql", response_type="ComDragonk8sTutorialV1PyMysql")
    # apigvk.register_gvk(ComDragonk8sTutorialV1PyMysql)

    # 加载k8s配置
    cfg = Configuration()
    # # 在集群外可以使用kubeconfig文件
    # config.load_kube_config(config_file="C:\\Users\\Administrator\\.kube\\config", client_configuration=cfg)
    # # 集群内可以直接初始化内置配置
    # config.load_incluster_config(client_configuration=cfg)
    config.load_kube_config(config_file="/Users/bytedance/mygit/deploy/0_config/my-k8s.conf", client_configuration=cfg)
    return CommonClient(configuration=cfg)


def get_service_client(client=None):
    if not client:
        client = init_client()
    return apigvk.get_resource_client(client, CoreV1Service)


class DragonClientTest(unittest.TestCase):

    def test_create(self):
        service_client = get_service_client()
        from kubernetes.client.models import V1Service, V1ObjectMeta, V1ServiceSpec, V1ServicePort
        svc = V1Service(
            api_version=CoreV1Service.group_version,
            kind=CoreV1Service.kind,
            metadata=V1ObjectMeta(
                name="test-service",
                namespace="default",
                labels={"app": "test"},
            ),
            spec=V1ServiceSpec(
                type="ClusterIP",
                selector={"app": "pod_label"},
                ports=[
                    V1ServicePort(
                        name="port1",
                        port=3306,
                        target_port=3306,
                    )
                ]
            )
        )
        created_svc = service_client.create(svc)
        print(created_svc)

    def test_get_with_name(self):
        client = init_client()
        CoreV1Service = apigvk.GVK(
            group="", version="v1", kind="Service", response_type="V1Service")
        service_client = apigvk.get_resource_client(client, CoreV1Service)
        svc = service_client.get(namespace="default", name="test-service")
        from kubernetes.client.models import V1Service, V1ObjectMeta
        assert isinstance(svc, V1Service)
        assert isinstance(svc.metadata, V1ObjectMeta)
        print(svc.spec)

    def test_list(self):
        client = init_client()
        CoreV1Service = apigvk.GVK(
            group="", version="v1", kind="Service", response_type="V1Service")
        service_client = apigvk.get_resource_client(client, CoreV1Service)
        svcs = service_client.list(namespace="default")
        from kubernetes.client.models import V1Service, V1ServiceList
        assert isinstance(svcs, V1ServiceList)
        assert isinstance(svcs.items[0], V1Service)
        print(len(svcs.items))

    def test_list_with_label(self):
        client = init_client()
        CoreV1Service = apigvk.GVK(
            group="", version="v1", kind="Service", response_type="V1Service")
        service_client = apigvk.get_resource_client(client, CoreV1Service)
        svcs = service_client.list(namespace="default", label_selector="app=test")
        from kubernetes.client.models import V1Service, V1ServiceList
        assert isinstance(svcs, V1ServiceList)
        assert isinstance(svcs.items[0], V1Service)
        print(len(svcs.items))
        print(svcs.items)

    def test_list_with_field(self):
        client = init_client()
        CoreV1Service = apigvk.GVK(
            group="", version="v1", kind="Service", response_type="V1Service")
        service_client = apigvk.get_resource_client(client, CoreV1Service)
        svcs = service_client.list(namespace="default", field_selector="metadata.name=test-service")
        from kubernetes.client.models import V1Service, V1ServiceList
        assert isinstance(svcs, V1ServiceList)
        assert isinstance(svcs.items[0], V1Service)
        print(len(svcs.items))
        print(svcs.items)

    def test_replace(self):
        client = init_client()
        CoreV1Service = apigvk.GVK(
            group="", version="v1", kind="Service", response_type="V1Service")
        service_client = apigvk.get_resource_client(client, CoreV1Service)
        svc = service_client.get(namespace="default", name="test-service")
        svc.metadata.labels = {"app": "test2"}
        service_client.replace(body=svc, name=svc.metadata.name, namespace=svc.metadata.namespace)

    def test_patch(self):
        client = init_client()
        CoreV1Service = apigvk.GVK(
            group="", version="v1", kind="Service", response_type="V1Service")
        service_client = apigvk.get_resource_client(client, CoreV1Service)
        data = {
            "metadata": {
                "labels": {"app": "test", "aa2": "bb2"}
            }
        }
        from dragonk8s.lib.apimachinery.pkg.types import patch
        service_client.patch(body=data, name="test-service", namespace="default", content_type=patch.PatchType.MergePatchType)

    def test_update_subresource(self):
        client = init_client()
        CoreV1Service = apigvk.GVK(
            group="", version="v1", kind="Service", response_type="V1Service")
        service_client = apigvk.get_resource_client(client, CoreV1Service)
        svc = service_client.get(namespace="default", name="test-service")
        from kubernetes.client.models import V1ServiceStatus, V1Condition
        svc.status = V1ServiceStatus(
            conditions=[V1Condition(
                reason="test",
                type="test",
                status="test_status",
                last_transition_time="2022-11-30T02:21:25.458481Z",
                message="test msg"
            )],
        )
        res = service_client.replace(body=svc, name=svc.metadata.name, namespace=svc.metadata.namespace)
        print(res)

    def test_watch(self):
        client = init_client()
        CoreV1Service = apigvk.GVK(
            group="", version="v1", kind="Service", response_type="V1Service")
        service_client = apigvk.get_resource_client(client, CoreV1Service)

        from dragonk8s.lib.client import CommonWatch
        from kubernetes.client.models import V1Service
        rs = "0"
        w = CommonWatch(common_client=service_client)
        th = threading.Thread(target=service_client.watch, kwargs=dict(
            resource_version=rs, namespace="default", timeout_seconds=5, watcher=w
        ))
        th.start()
        while True:
            print("+++------------------------------------------")
            try:
                e = w.get_result_queue().get(block=True, timeout=5)
            except queue.Empty:
                continue
            if not e:
                continue
            print(e['type'])
            assert isinstance(e['object'], V1Service)

    def test_delete(self):
        client = init_client()
        CoreV1Service = apigvk.GVK(
            group="", version="v1", kind="Service", response_type="V1Service")
        service_client = apigvk.get_resource_client(client, CoreV1Service)
        svc = service_client.delete(namespace="default", name="test-service")
        print(svc)