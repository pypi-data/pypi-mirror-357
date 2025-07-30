import unittest


class _WaitFor(object):

    def __init__(self, data, ready_at):
        self.data = data
        self.ready_at = ready_at
        self.index = 0


class _PriorityQueue(object):

    def __init__(self, size=1000):
        self._data = [_WaitFor(None, 0)] * size
        self._size = size
        self._len = 0

    def is_full(self):
        return self._len == self._size

    def is_empty(self):
        return self._len == 0

    def add(self, x: _WaitFor):
        if self.is_full():
            raise Exception("is full")
        i = self._len
        self._len += 1
        while i > 0:
            p = int((i-1)/2)
            if self._data[p].ready_at <= x.ready_at:
                break
            self._data[i] = self._data[p]
            i = p
        self._data[i] = x

    def get(self) -> _WaitFor|None:
        if self.is_empty():
            return None
        res = self._data[0]
        i = 0
        x = self._data[self._len-1]
        self._len -= 1
        while 2 * i + 1 < self._len:
            a = 2 * i + 1
            b = 2 * i + 2
            if b < self._len and self._data[b].ready_at < self._data[a].ready_at:
                a = b
            if x.ready_at < self._data[a].ready_at:
                break
            self._data[i] = self._data[a]
            i = a
        self._data[i] = x
        return res


class UtilTest(unittest.TestCase):

    def test1(self):
        p = _PriorityQueue()
        p.add(_WaitFor(1, 1))
        p.add(_WaitFor(2, 2))
        p.add(_WaitFor(10, 10))
        p.add(_WaitFor(8, 8))

        print(p.get().ready_at)
        print(p.get().ready_at)
        print(p.get().ready_at)
        print(p.get().ready_at)


