from __future__ import annotations

import copy

from kubernetes.client.models import V1LabelSelector, V1ObjectMeta, V1OwnerReference
from dragonk8s.lib.apimachinery.pkg import labels
from dragonk8s.lib.apimachinery.pkg.selection import Operator


NamespaceDefault = "default"
NamespaceAll = ""
NamespaceNone = ""
NamespaceSystem = "kube-system"
NamespacePublic = "kube-public"

StatusSuccess = "Success"
StatusFailure = "Failure"

LabelSelectorOpIn = "in"
LabelSelectorOpNotIn = "notin"
LabelSelectorOpExists = "exists"
LabelSelectorOpDoesNotExist = "doesnotexist"


def get_controller_of_no_copy(controllee) -> V1OwnerReference|None:
    refs = controllee.metadata.owner_references
    if not refs:
        return None
    for r in refs:
        if r.controller is True:
            return r
    return None


def get_controller_of(controllee) -> V1OwnerReference:
    res = get_controller_of_no_copy(controllee)
    return copy.copy(res)


def new_controller_ref(owner, gvk) -> V1OwnerReference:
    return V1OwnerReference(
        api_version=gvk.group_version,
        kind=gvk.kind,
        name=owner.metadata.name,
        uid=owner.metadata.uid,
        block_owner_deletion=True,
        controller=True,
    )


class TypeMeta(object):

    def __init__(self, kind="", api_version=""):
        self.kind = kind
        self.api_version = api_version


class ResourceVersionMatch(object):

    NotOlderThan = "NotOlderThan"
    Exact = "Exact"


class ListOptions(TypeMeta):

    def __init__(self, kind="", api_version="", label_selector="", field_selector="", watch=False,
                 allow_watch_bookmarks=False, resource_version="", resource_version_match=ResourceVersionMatch.Exact,
                 timeout_seconds=10, limit=10, _continue=""):
        super().__init__(kind, api_version)
        self.label_selector = label_selector
        self.field_selector = field_selector
        self.watch = watch
        self.allow_watch_bookmarks = allow_watch_bookmarks
        self.resource_version = resource_version
        self.resource_version_match = resource_version_match
        self.timeout_seconds = timeout_seconds
        self.limit = limit
        self._continue = _continue

    def to_params(self):
        return dict(
            label_selector=self.label_selector,
            field_selector=self.field_selector,
            resource_version=self.resource_version,
            timeout_seconds=self.timeout_seconds,
        )


class ListMeta(object):

    def __init__(self, self_link, resource_version, _continue, remaining_item_count):
        self.self_link = self_link
        self.resource_version = resource_version
        self._continue = _continue
        self.remaining_item_count = remaining_item_count


def labels_selector_as_selector(ps: V1LabelSelector) -> labels.Selector:
    if ps is None:
        return labels.nothing
    if ps.match_labels is None:
        ps.match_labels = {}
    if ps.match_expressions is None:
        ps.match_expressions = []
    if len(ps.match_labels) + len(ps.match_expressions) == 0:
        return labels.every_thing
    requirements = []
    for k, v in ps.match_labels.items():
        r = labels.new_requirement(k, Operator.Equals, [v])
        requirements.append(r)
    for expr in ps.match_expressions:
        op = None
        if expr.operator.lower() == LabelSelectorOpIn:
            op = Operator.In
        elif expr.operator.lower() == LabelSelectorOpNotIn:
            op = Operator.NotIn
        elif expr.operator.lower() == LabelSelectorOpExists:
            op = Operator.Exists
        elif expr.operator.lower() == LabelSelectorOpDoesNotExist:
            op = Operator.DoesNotExist
        else:
            raise Exception("%s is not a valid pod selector operator" % expr.operator)
        r = labels.new_requirement(expr.key, op, copy.copy(expr.values))
        requirements.append(r)
    selector = labels.new_selector()
    selector = selector.add(*requirements)
    return selector
