import logging
import threading
import time
import unittest
from dragonk8s.lib.client.informers import factory
from dragonk8s.lib.apimeta import apigvk
from dragonk8s.lib.client.informers.informer import get_informer
from kubernetes import config
from dragonk8s.lib.client import CommonClient
from dragonk8s.lib.client.configuration import Configuration
from dragonk8s.lib.client.tools import informer
from dragonk8s.lib.client.tools import cache


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


class DragonInformerTest(unittest.TestCase):

    def test_informer(self):
        client = init_client()
        stop = threading.Event()
        informer_factory = factory.SharedInformerFactory(client, default_resync=0, stop=stop)
        service_informer = get_informer(CoreV1Service, informer_factory)

        def add(obj):
            print("add obj: %s/%s" %(obj.metadata.namepace, obj.metadata.name))

        def update(old, new):
            print("update obj: %s/%s" % (obj.metadata.namepace, obj.metadata.name))

        def delete(obj):
            if isinstance(obj, cache.DeletedFinalStateUnknown):
                obj = obj.obj
            print("delete obj: %s/%s" % (obj.metadata.namepace, obj.metadata.name))

        service_informer.informer().add_event_handler(informer.ResourceEventHandlerFuncs(
            add_func=add,
            update_func=update,
            delete_func=delete,
        ))
        service_lister = service_informer.lister()

        informer_factory.start(stop)
        informer_factory.wait_for_cache_sync(stop)
        print("all synced")
        while True:
            time.sleep(5)
            service_lister.list()
            service_lister.with_namespace("default").get("test-service")
