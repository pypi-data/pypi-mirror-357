import unittest
from dragonk8s.lib.client.tools import cache


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
        rs_cache = cache.Cache.new_Store(cache.meta_namespace_key_func)
        rs_cache.add(self.get_service("s1", "n1"))
        rs_cache.add(self.get_service("s2", "n2"))
        svc, exist = rs_cache.get_by_key("n1/s1")
        self.assertTrue(exist)
        self.assertEqual(svc.metadata.name, "s1")

        keys = rs_cache.list_keys()
        self.assertEqual(set(keys), {"n1/s1", "n2/s2"})

    def test_index(self):
        rs_cache = cache.Cache.new_Store(cache.meta_namespace_key_func)

        def ns_index(obj):
            return [obj.metadata.namespace]
        rs_cache.add_indexers({"ns": ns_index})

        rs_cache.add(self.get_service("s1", "n1"))
        rs_cache.add(self.get_service("s2", "n2"))
        rs_cache.add(self.get_service("s3", "n1"))

        keys = rs_cache.index_keys("ns", "n1")
        self.assertEqual(set(keys), {'n1/s1', 'n1/s3'})