from dragonk8s.lib.client.tools.record import EventSink
from kubernetes.client.models.core_v1_event import CoreV1Event
from kubernetes import client


class EventSinkImpl(EventSink):

    def __init__(self):
        super().__init__()
        self.client = client.CoreV1Api()

    def create(self, event: CoreV1Event) -> CoreV1Event:

        return self.client.create_namespaced_event(event.metadata.namespace, event)

    def update(self, event: CoreV1Event) -> CoreV1Event:
        return self.client.replace_namespaced_event(event.metadata.name, event.metadata.namespace, event)

    def patch(self, old_event: CoreV1Event, data) -> CoreV1Event:
        return self.client.patch_namespaced_event(old_event.metadata.name, old_event.metadata.namespace, data)
