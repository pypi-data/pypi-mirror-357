from threading import Event
from dragonk8s.lib.apimachinery.pkg.apis import meta_v1
from dragonk8s.lib.apimachinery.pkg.apis import meta_internal_version
from kubernetes.client.exceptions import ApiException
from dragonk8s.lib.apimachinery.pkg.api import errors, meta


def simple_page_func(fn):
    def do(stop: Event, options:meta_v1.ListOptions):
        return fn(options)
    return do


class ListPager(object):

    def __init__(self, page_fn, page_size=500, full_list_if_expired=True, page_buffer_size=10):
        self.page_size = page_size
        self.page_fn = page_fn
        self.full_list_if_expired = full_list_if_expired
        self.page_buffer_size = page_buffer_size

    def list(self, options:meta_v1.ListOptions, stop: Event):
        if options.limit == 0:
            options.limit = self.page_size

        requested_resource_version = options.resource_version
        requested_resource_version_match = options.resource_version_match
        paginated_result = False
        rlist = None

        while True:
            if stop.is_set():
                return None, paginated_result
            try:
                obj = self.page_fn(stop, options)
            except ApiException as e:
                if not errors.is_resource_expired(e) or not self.full_list_if_expired or options._continue == "":
                    return None, paginated_result
                options.limit = 0
                options._continue = ""
                options.resource_version = requested_resource_version
                options.resource_version_match = requested_resource_version_match
                return self.page_fn(stop, options), paginated_result
            except Exception as e:
                return None, paginated_result
            try:
                m = meta.list_accessor(obj)
            except Exception as e:
                raise Exception("returned object is not standard list: " + str(e))
            if not m._continue and rlist is None:
                return obj, paginated_result
            options._continue = m._continue
            options.resource_version = ""
            options.resource_version_match = ""
            paginated_result = True
