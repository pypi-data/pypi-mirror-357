import unittest
import time
from dragonk8s.lib.util import timeutil
import queue


class UtilTest(unittest.TestCase):

    def test1(self):
        now = 1671851469.805154
        self.assertEqual('2022-12-24T11:11:09.805154Z', timeutil.to_time_str_with_ns(now))

    def test2(self):
        q = queue.Queue(2)
        q.put("a",  True, 5)
        print(q.qsize())
        print(q.get(True, 5))
        print(q.qsize())
        print(q.get(True, 5))