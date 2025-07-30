from dragonk8s.lib.apimachinery.pkg.apis import meta_v1


class List(object):

    def __init__(self, type_meta, list_meta, items):
        self.type_meta = type_meta
        self.list_meta = list_meta
        self.items = items