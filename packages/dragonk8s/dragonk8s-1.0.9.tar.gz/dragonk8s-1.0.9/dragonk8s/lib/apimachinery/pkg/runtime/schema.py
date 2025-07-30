import string


class GroupKind(object):

    def __init__(self, group="", kind=""):
        self.group = group
        self.kind = kind

    def empty(self) -> bool:
        return self.group == "" and self.kind == ""

    def __str__(self):
        if self.group == "":
            return self.kind
        return "%s.%s" %(self.kind, self.group)


class GroupVersionKind(object):

    def __init__(self, group="", version="", kind=""):
        self.group = group
        self.version = version
        self.kind = kind

    def empty(self) -> bool:
        return self.group == "" and self.version == "" and self.kind == ""

    def __str__(self):
        return "%s/%s, kind=%s" % (self.group, self.version, self.kind)


class GroupVersion(object):

    def __init__(self, group="", version=""):
        self.group = group
        self.version = version

    def empty(self) -> bool:
        return self.group == "" and self.version == ""

    def __str__(self):
        if self.group != "":
            return "%s/%s" % (self.group, self.version)
        return self.version

    def identifier(self):
        return str(self)


def parse_group_version(gv: str) -> GroupVersion:
    if len(gv) == 0 or gv == "/":
        return GroupVersion()
    c = gv.count("/")
    if c == 0:
        return GroupVersion(group="", version=gv)
    if c == 1:
        i = gv.index("/")
        return GroupVersion(group=gv[:i], version=gv[i+1:])
    raise Exception("unexpected GroupVersion string: %s", gv)


def from_api_version_and_kind(api_version: str, kind: str) -> GroupVersionKind:
    try:
        gv = parse_group_version(api_version)
        return GroupVersionKind(group=gv.group, version=gv.version, kind=kind)
    except:
        return GroupVersionKind(kind=kind)


def from_obj(obj) -> GroupVersionKind:
    if obj is None:
        return GroupVersionKind()
    api_version = ""
    kind = ""
    if hasattr(obj, "api_version"):
        api_version = obj.api_version
    if hasattr(obj, "kind"):
        kind = obj.kind
    return from_api_version_and_kind(api_version, kind)
