from kubernetes.client.models.v1_object_reference import V1ObjectReference
from dragonk8s.lib.apimachinery.pkg.runtime import schema


def get_reference(obj) -> V1ObjectReference:
    if obj is None:
        raise Exception("obj is None")
    if isinstance(obj, V1ObjectReference):
        return obj
    api_version = getattr(obj, "api_version")
    kind = getattr(obj, "kind")
    gvk = schema.from_api_version_and_kind(api_version, kind)
    if gvk.empty():
        raise Exception("unexecpeced gvks from obj: %s" % obj)
    object_meta = getattr(obj, "metadata")
    if object_meta is None:
        return V1ObjectReference(kind=kind, api_version=api_version)
    return V1ObjectReference(
        kind=kind,
        api_version=api_version,
        name=object_meta.name,
        namespace=object_meta.namespace,
        uid=object_meta.uid,
        resource_version=object_meta.resource_version,
    )
