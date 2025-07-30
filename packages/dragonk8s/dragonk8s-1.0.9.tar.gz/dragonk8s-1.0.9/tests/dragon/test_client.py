import json
import threading
import time
import unittest
from kubernetes import config, dynamic
from kubernetes.client import models, configuration, api_client
from dragonk8s.dragon.models import *
from dragonk8s.dragon.models import IoDragonAppsV1ReplicaSetList, IoDragonAppsV1ReplicaSetStatus
from dragonk8s.lib.client import CommonClient, CommonWatch
from dragonk8s.dragon.api_client import ApiClient
from dragonk8s.lib.client.configuration import Configuration
from kubernetes.client.models import V1ReplicaSet
from kubernetes.client.apis import CoreV1Api
from kubernetes.client.api import CoreApi
from kubernetes.client.models import V1ObjectMeta
from kubernetes import watch
"""
1. 在dragon.models.__init__.py中加上
from kubernetes.client.models import *
2. 在dragon.configuration.py中修改self.client_side_validation=false
"""


class DragonClientTest(unittest.TestCase):

    def setUp(self):
        cfg = Configuration()
        # config.load_kube_config(config_file="C:\\Users\\Administrator\\.kube\\config", client_configuration=cfg)
        config.load_kube_config(config_file="/Users/bytedance/mygit/deploy/0_config/my-k8s.conf", client_configuration=cfg)
        Configuration.set_default(cfg)
        self.base_client = ApiClient()
        # client = dynamic.DynamicClient(
        #     self.base_client
        # )
        # config.load_kube_config(config_file="/Users/bytedance/.kube/config")
        # self.base_client = api_client.ApiClient()
        try:
            client = CommonClient()
            # client2 = dynamic.DynamicClient(self.base_client)
            self.client = client.resources.get(api_version="apps.dragon.io/v1", kind="ReplicaSet")
            # self.client2 = client2.resources.get(api_version="apps.dragon.io/v1", kind="ReplicaSet")

        except EOFError as e:
            print(e)

    def test_create(self):
        expressions = IoDragonAppsV1JobSpecSelectorMatchExpressions(
                        key="key",
                        operator="in",
                        values=["v1"]
                    )
        rs = IoDragonAppsV1ReplicaSet(
            api_version="apps.dragon.io/v1",
            kind="ReplicaSet",
            metadata=models.v1_object_meta.V1ObjectMeta(
                namespace="default",
                name="test30"
            ),
            spec=IoDragonAppsV1ReplicaSetSpec(
                min_ready_seconds=111,
                replicas=1,
                selector=IoDragonAppsV1JobSpecSelector(
                    match_expressions=[expressions]
                )
            )
        )
        rss = self.client.create(rs)
        print(rss.metadata)
        print(rss.api_version)
        # print(self.base_client.sanitize_for_serialization(rs))
        # self.client.create(self.base_client.sanitize_for_serialization(rs))

    def test_get(self):
        res = self.client.get(name="tt1", namespace="default")
        print(res)

    def test_patch(self):
        data = {
            "metadata": {
                "labels": {"app": "test", "aa2": "bb2"}
            }
        }
        res = self.client.patch(body=data, name="test30", namespace="default", content_type="application/merge-patch+json")
        print(res)

    def test_list(self):
        try:
            res = self.client.list()
        except Exception as e:
            print(str(e))
            return
        print(res)
        for r in res.items:
            print("{}: {}".format(r.metadata.name, res.metadata.resource_version))
            print(res.api_version)

    def test_subresource(self):
        res = self.client.get(name="test19", namespace="default")
        status = IoDragonAppsV1ReplicaSetStatus(
            available_replicas=1,
            replicas=0,
            ready_replicas=2,
            fully_labeled_replicas=0,
            conditions=[],
        )
        res.status = status
        rs = self.client.status.replace(name="test19", namespace="default", body=res)
        print(rs)


    """
    超过最新的报
    HTTP response body: {"kind":"Status","apiVersion":"v1","metadata":{},"status":"Failure","message":"Timeout: Too large resource version: 12313646, current: 12313645","reason":"Timeout","details":{"causes":[{"reason":"ResourceVersionTooLarge","message":"Too large resource version"}],"retryAfterSeconds":1},"code":504}
    """
    def test_list_by_resource_version(self):
        res = self.client.list(namespace="default", resource_version="0")
        print(res.metadata.resource_version)
        for r in res.items:
            print("{}: {}".format(r.metadata.name, res.metadata.resource_version))

    def test_watch(self):
        rs = "0"
        w = watch.Watch()
        while True:
            for e in self.client2.watch(resource_version=rs, namespace="default", timeout=5, watcher=w):
                print("------------------------------------------")
                if e['object'] is not None:
                    rs = e['object'].metadata.resourceVersion
                    print("===")
                    print(self.client.parse(e['object']))

    def test_watch2(self):
        rs = "0"
        w = CommonWatch(common_client=self.client)
        while True:
            print("+++------------------------------------------")
            for e in self.client.watch(resource_version=rs, namespace="default", timeout_seconds=5, watcher=w):
                print("------------------------------------------")
                if e['object'] is not None:
                    rs = e['object'].metadata.resource_version
                    print("===")
                    print(e['object'])

    def test_delete(self):
        res = self.client.delete(name="test29", namespace="default")
        print(res)


    def test(self):
        res = CommonClient(self.base_client).resources.get(api_version="apps/v1", kind="ControllerRevision").list()
        for r in res.items:
            print("{}".format(r))