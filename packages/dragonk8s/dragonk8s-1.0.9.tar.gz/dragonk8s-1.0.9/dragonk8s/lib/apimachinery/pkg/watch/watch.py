from queue import Queue


class Interface(object):

    def stop(self):
        pass

    def get_result_queue(self) -> Queue:
        pass


class EventType(object):
    Added = "ADDED"
    Modified = "MODIFIED"
    Deleted = "DELETED"
    Bookmark = "BOOKMARK"
    Error = "ERROR"
    End = "End"


class Event(object):

    def __init__(self, _type: str = EventType.Added, obj=None):
        self.type = _type
        self.obj = obj
