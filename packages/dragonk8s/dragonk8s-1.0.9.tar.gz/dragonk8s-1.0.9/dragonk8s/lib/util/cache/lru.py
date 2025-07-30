

class Entry(object):

    def __init__(self, key, value):
        self.key = key
        self.value = value


class Cache(object):

    def __init__(self, max_entries: int):
        self.max_entries = max_entries
        self._ll = []
        self._cache = dict()
        self.on_evicted = None

    def _move_to_front(self, entry: Entry):
        self._ll.remove(entry)
        self._ll.append(entry)

    def _push_front(self, entry):
        self._ll.append(entry)

    def remove_oldest(self):
        if len(self._ll) == 0:
            return
        entry = self._ll[0]
        self._remove_element(entry)

    def add(self, key, value):
        if key in self._cache:
            self._move_to_front(self._cache[key])
            self._cache[key].value = value
            return
        entry = Entry(key, value)
        self._push_front(entry)
        self._cache[key] = entry
        if 0 < self.max_entries < len(self._ll):
            self.remove_oldest()

    def get(self, key):
        if key in self._cache:
            self._move_to_front(self._cache[key])
            return self._cache[key].value, True
        return None, False

    def _remove_element(self, entry: Entry):
        self._ll.remove(entry)
        del self._cache[entry.key]
        if self.on_evicted is not None:
            self.on_evicted(entry.key, entry.value)

    def remove(self, key):
        if key in self._cache:
            self._remove_element(self._cache[key])

    def __len__(self):
        return len(self._ll)

    def clear(self):
        if self.on_evicted is not None:
            for k, entry in self._cache.items():
                self.on_evicted(entry.key, entry.value)
        self._ll.clear()
        self._cache.clear()
