import json
import threading
import time
import unittest
from kubernetes import config, dynamic
from kubernetes.client import models, configuration, api_client
from dragonk8s.dragon.models import *
from dragonk8s.dragon.models import IoDragonAppsV1ReplicaSetList
from kubernetes.client import V1ListMeta
from dragonk8s.lib.client import CommonClient, CommonWatch
from dragonk8s.dragon.api_client import ApiClient
from dragonk8s.dragon.configuration import Configuration
from kubernetes.client.models import V1ReplicaSet
from kubernetes.client.apis import CoreV1Api
from kubernetes.client.api import CoreApi
from kubernetes.client.models import V1ObjectMeta
from kubernetes import watch
from dragonk8s.lib.client.informers.dragon import replicaset
from dragonk8s.lib.client.tools.informer import ResourceEventHandler
from dragonk8s.lib.client.informers import factory
from dragonk8s.lib.apimeta import apigvk
from dragonk8s.lib.apimachinery.pkg import labels
from dragonk8s.lib.client.informers.informer import get_informer


class MyHandler(ResourceEventHandler):
    def on_add(self, obj):
        print("add %s" % obj.metadata.name)

    def on_update(self, old_obj, new_obj):
        print("update %s" % new_obj.metadata.name)

    def on_delete(self, obj):
        print("delete %s" % obj.metadata.name)


class DragonInformerTest(unittest.TestCase):

    def setUp(self):
        cfg = Configuration()
        config.load_kube_config(config_file="C:\\Users\\Administrator\\.kube\\config", client_configuration=cfg)
        Configuration.set_default(cfg)
        self.base_client = ApiClient()
        try:
            self.client = CommonClient(self.base_client)

        except EOFError as e:
            print(e)

    def test_infromer(self):
        informer = replicaset.new_replica_set_informer(self.client, "default", 0, {})
        informer.add_event_handler_with_resync_period(MyHandler(), 0)
        stop = threading.Event()
        t = threading.Thread(target=informer.run, args=(stop,))
        t.start()
        n = 0
        sync = False
        while n < 20:
            if informer.has_synced():
                print("synced------")
                sync = True
                break
            else:
                n += 1
                time.sleep(1)
        if not sync:
            raise Exception("not sync")

        t.join()

    def test_infromer2(self):
        informer = factory.new_informer(self.client, apigvk.IoDragonAppsV1ReplicaSet,  "default", 0, {}, threading.Event())
        informer.add_event_handler_with_resync_period(MyHandler(), 0)
        stop = threading.Event()
        t = threading.Thread(target=informer.run, args=(stop,))
        t.start()
        n = 0
        sync = False
        while n < 20:
            if informer.has_synced():
                print("synced------")
                sync = True
                break
            else:
                n += 1
                time.sleep(1)
        if not sync:
            raise Exception("not sync")

        t.join()

    def test_infromer3(self):
        f = factory.SharedInformerFactory(self.client, default_resync=0)


        informer = f.informer_for(apigvk.IoDragonAppsV1ReplicaSet)
        informer.add_event_handler_with_resync_period(MyHandler(), 0)
        stop = threading.Event()
        f.start(stop)
        f.wait_for_cache_sync(stop)
        print("wait done")
        time.sleep(100)

    def test_informer4(self):
        f = factory.SharedInformerFactory(self.client, default_resync=0)
        inf = replicaset.ReplicaSetInformer(f)
        informer = inf.informer()
        lister = inf.lister()
        informer.add_event_handler_with_resync_period(MyHandler(), 0)
        stop = threading.Event()
        f.start(stop)
        f.wait_for_cache_sync(stop)
        print("wait done")

        rss = lister.list(labels.every_thing)
        print(len(rss))
        rs = lister.with_namespace("default").get("tt1")
        print(rs)
        time.sleep(100)

    def test_informer5(self):
        f = factory.SharedInformerFactory(self.client, default_resync=0)
        inf = get_informer(apigvk.CoreV1Pod, f)
        informer = inf.informer()
        lister = inf.lister()
        informer.add_event_handler_with_resync_period(MyHandler(), 0)
        stop = threading.Event()
        f.start(stop)
        f.wait_for_cache_sync(stop)
        print("wait done")

        # rss = lister.list(labels.every_thing)
        # print(len(rss))
        # for rs in rss:
        #     print(rs)
        #     print("--------------")
        time.sleep(100)
