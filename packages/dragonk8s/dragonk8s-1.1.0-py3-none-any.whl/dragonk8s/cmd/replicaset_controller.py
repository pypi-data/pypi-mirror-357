import logging
import os
import sys
import threading
import signal
from dragonk8s.lib.client.informers import factory
from dragonk8s.lib.apimeta import apigvk
from dragonk8s.lib.client.informers.informer import get_informer
from dragonk8s.lib.client.informers.dragon.replicaset import ReplicaSetInformer
from kubernetes import config
from dragonk8s.lib.client import CommonClient
from dragonk8s.dragon.configuration import Configuration
from dragonk8s.pkg.controller.replicaset.replica_set import ReplicaSetController
from dragonk8s.lib.pool import thread_manager

stop = threading.Event()
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(thread)d %(filename)s-%(lineno)d(%(funcName)s): %(message)s")


def init_client() -> CommonClient:
    cfg = Configuration()
    if 'sys' in os.environ and os.environ['sys'] == "local":
        config.load_kube_config(config_file="C:\\Users\\Administrator\\.kube\\config", client_configuration=cfg)
    elif 'sys' in os.environ and os.environ['sys'] == "mac":
        config.load_kube_config(config_file="/Users/bytedance/mygit/deploy/0_config/my-k8s.conf", client_configuration=cfg)
    else:
        config.load_incluster_config(client_configuration=cfg)
    client = CommonClient(configuration=cfg)
    return client


def exit_handler(signum, frame):
    logging.info("exit with signal.")
    if not stop.is_set():
        logging.info("set stop event.")
        stop.set()
        res = thread_manager.GlobalThreadManager.wait_stop_and_clean(10)
        if res:
            sys.exit(0)
        else:
            sys.exit(1)


def init_signal():
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)


def main():
    client = init_client()
    init_signal()
    f = factory.SharedInformerFactory(client, default_resync=0, stop=stop)
    pod_informer = get_informer(apigvk.CoreV1Pod, f)
    replicaset_informer = ReplicaSetInformer(informer_factory=f)
    replicaset_controller = ReplicaSetController(replicaset_informer, pod_informer, client, 300, stop)
    f.start(stop)
    f.wait_for_cache_sync(stop)
    replicaset_controller.run(1)


if __name__ == '__main__':
    main()
