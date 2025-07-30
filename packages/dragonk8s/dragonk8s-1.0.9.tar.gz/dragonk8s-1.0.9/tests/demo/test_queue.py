import time
import unittest
from dragonk8s.lib.client.util.workqueue import RateLimitingType, default_rate_limiter


class DragonCacheTest(unittest.TestCase):

    def get_service(self, name, namespace):
        from kubernetes.client.models import V1Service, V1ObjectMeta
        return V1Service(
            metadata=V1ObjectMeta(
                name=name,
                namespace=namespace,
            )
        )

    def test_basic(self):
        queue = RateLimitingType(rate_limiter=default_rate_limiter())

        queue.add("1")
        queue.add("2")
        queue.add_after("3", 1)
        queue.add_rate_limited("4")

        while queue.len() > 0:
            print(queue.get())
        print("---")
        time.sleep(10)
        while queue.len() > 0:
            print(queue.get())
        queue.shutdown()

