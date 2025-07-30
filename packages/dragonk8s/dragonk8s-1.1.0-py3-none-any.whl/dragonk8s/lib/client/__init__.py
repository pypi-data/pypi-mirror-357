import json
import six
from kubernetes.dynamic.client import DynamicClient, ResourceInstance, ApiException, api_exception
from dragonk8s.lib.client.api_client import ApiClient
from dragonk8s.lib.apimeta import apigvk
from kubernetes.watch.watch import Watch, SimpleNamespace
from dragonk8s.lib.apimachinery.pkg.watch import watch
from queue import Queue


class SimpleBody(object):

    def __init__(self, data):
        self.data = data


def meta_request(func):
    """ Handles parsing response structure and translating API Exceptions """
    def inner(self, *args, **kwargs):
        serialize_response = kwargs.get('serialize', True)
        serializer = kwargs.get('serializer', ResourceInstance)
        if "watch" in kwargs and kwargs["watch"]:
            kwargs.pop("response_type")
        if 'response_type' in kwargs and kwargs['response_type'] is not None and kwargs['response_type'] != "":
            serialize_response = False
        try:
            resp = func(self, *args, **kwargs)
        except ApiException as e:
            raise api_exception(e)
        if serialize_response:
            try:
                if six.PY2:
                    return serializer(self, json.loads(resp.data))
                return serializer(self, json.loads(resp.data.decode('utf8')))
            except ValueError:
                if six.PY2:
                    return resp.data
                return resp.data.decode('utf8')
        return resp

    return inner


class CommonWatch(Watch, watch.Interface):

    def __init__(self, common_client):
        super(CommonWatch, self).__init__(return_type=None)
        self.common_client = common_client
        self.queue = Queue()

    def stop(self):
        pass

    def get_result_queue(self) -> Queue:
        return self.queue

    def unmarshal_event(self, data, return_type):
        js = json.loads(data)
        js['raw_object'] = js['object']
        # BOOKMARK event is treated the same as ERROR for a quick fix of
        # decoding exception
        # TODO: make use of the resource_version in BOOKMARK event for more
        # efficient WATCH
        if js['type'] != 'ERROR' and js['type'] != 'BOOKMARK':
            obj = js['raw_object']
            js['object'] = self.common_client.parse(obj)
            if hasattr(js['object'], 'metadata'):
                self.resource_version = js['object'].metadata.resource_version
            # For custom objects that we don't have model defined, json
            # deserialization results in dictionary
            elif (isinstance(js['object'], dict) and 'metadata' in js['object']
                  and 'resourceVersion' in js['object']['metadata']):
                self.resource_version = js['object']['metadata'][
                    'resourceVersion']
        return js


class CommonClient(DynamicClient):

    def _get_response_type_list(self, response_type):
        return "{}List".format(response_type)

    def __init__(self, cache_file=None, discoverer=None, configuration=None):
        client = ApiClient(configuration=configuration)

        super().__init__(client, cache_file, discoverer)
        self.response_type_map = {}
        self.init_response_type()
        apigvk.register_model_package()

    def init_response_type(self):
        for gvk in apigvk.ALL:
            self.register_response_type(api_version=gvk.group_version, kind=gvk.kind, response_type=gvk.response_type)

    def get_response_type(self, api_version: str, kind: str) -> str:
        key = "{}/{}".format(api_version, kind)
        if key not in self.response_type_map:
            return ""
        rt = self.response_type_map[key]
        return rt

    def get_response_type_list(self, api_version: str, kind: str) -> str:
        key = "{}/{}".format(api_version, kind)
        if key not in self.response_type_map:
            return ""
        rt = self.response_type_map[key]
        return self._get_response_type_list(rt)

    def register_response_type(self,  api_version: str, kind: str, response_type: str):
        key = "{}/{}".format(api_version, kind)
        self.response_type_map[key] = response_type

    def serialize_body(self, body):
        return body

    def ensure_namespace(self, resource, namespace, body):
        if not namespace:
            if hasattr(body, "metadata"):
                namespace = body.metadata.namespace
        if not namespace:
            raise ValueError("Namespace is required for {}.{}".format(resource.group_version, resource.kind))
        return namespace

    def list(self, resource, namespace=None, **kwargs):
        path = resource.path(name=None, namespace=namespace)
        return self.request('get', path, response_type=self.get_response_type_list(resource.group_version, resource.kind), **kwargs)

    def get(self, resource, name=None, namespace=None, **kwargs):
        return super(CommonClient, self).get(
            resource, name=name, namespace=namespace, response_type=self.get_response_type(resource.group_version, resource.kind), **kwargs)

    def create(self, resource, body=None, namespace=None, **kwargs):
        return super(CommonClient, self).create(
            resource, body=body, namespace=namespace, response_type=self.get_response_type(resource.group_version, resource.kind), **kwargs)

    def delete(self, resource, name=None, namespace=None, body=None, label_selector=None, field_selector=None, **kwargs):
        return super(CommonClient, self).delete(resource, name=name, namespace=namespace, body=body,
                                                label_selector=label_selector, field_selector=field_selector,
                                                response_type=self.get_response_type(resource.group_version, resource.kind), **kwargs)

    def replace(self, resource, body=None, name=None, namespace=None, **kwargs):
        return super(CommonClient, self).replace(resource, body=body, name=name, namespace=namespace,
                                                 response_type=self.get_response_type(resource.group_version, resource.kind), **kwargs)

    def patch(self, resource, body=None, name=None, namespace=None, **kwargs):
        return super(CommonClient, self).patch(resource, body=body, name=name, namespace=namespace,
                                               response_type=self.get_response_type(resource.group_version, resource.kind), **kwargs)

    def watch(self, resource, namespace=None, name=None, label_selector=None, field_selector=None,
              resource_version=None, timeout_seconds=None, watcher=None):
        """
        Stream events for a resource from the Kubernetes API

        :param resource: The API resource object that will be used to query the API
        :param namespace: The namespace to query
        :param name: The name of the resource instance to query
        :param label_selector: The label selector with which to filter results
        :param field_selector: The field selector with which to filter results
        :param resource_version: The version with which to filter results. Only events with
                                 a resource_version greater than this value will be returned
        :param timeout_seconds: The amount of time in seconds to wait before terminating the stream
        :param watcher: The Watcher object that will be used to stream the resource

        :return: Event object with these keys:
                   'type': The type of event such as "ADDED", "DELETED", etc.
                   'raw_object': a dict representing the watched object.
                   'object': A ResourceInstance wrapping raw_object.

        Example:
            client = DynamicClient(k8s_client)
            watcher = watch.Watch()
            v1_pods = client.resources.get(api_version='v1', kind='Pod')

            for e in v1_pods.watch(resource_version=0, namespace=default, timeout=5, watcher=watcher):
                print(e['type'])
                print(e['object'].metadata)
                # If you want to gracefully stop the stream watcher
                watcher.stop()
        """
        if not watcher: watcher = CommonWatch(self)
        cnt = 0
        for event in watcher.stream(
            resource.get,
            namespace=namespace,
            name=name,
            field_selector=field_selector,
            label_selector=label_selector,
            resource_version=resource_version,
            serialize=False,
            timeout_seconds=timeout_seconds,
            watch=True,
        ):
            cnt += 1
            watcher.get_result_queue().put(event)
        if cnt == 0:
            return None
        watcher.get_result_queue().put({
            "type": watch.EventType.End
        })
        return watcher

    @meta_request
    def request(self, method, path, body=None, **params):
        if not path.startswith('/'):
            path = '/' + path

        path_params = params.get('path_params', {})
        query_params = params.get('query_params', [])
        if params.get('pretty') is not None:
            query_params.append(('pretty', params['pretty']))
        if params.get('_continue') is not None:
            query_params.append(('continue', params['_continue']))
        if params.get('include_uninitialized') is not None:
            query_params.append(('includeUninitialized', params['include_uninitialized']))
        if params.get('field_selector') is not None:
            query_params.append(('fieldSelector', params['field_selector']))
        if params.get('label_selector') is not None:
            query_params.append(('labelSelector', params['label_selector']))
        if params.get('limit') is not None:
            query_params.append(('limit', params['limit']))
        if params.get('resource_version') is not None:
            query_params.append(('resourceVersion', params['resource_version']))
        if params.get('timeout_seconds') is not None:
            query_params.append(('timeoutSeconds', params['timeout_seconds']))
        if params.get('watch') is not None:
            query_params.append(('watch', params['watch']))
        if params.get('grace_period_seconds') is not None:
            query_params.append(('gracePeriodSeconds', params['grace_period_seconds']))
        if params.get('propagation_policy') is not None:
            query_params.append(('propagationPolicy', params['propagation_policy']))
        if params.get('orphan_dependents') is not None:
            query_params.append(('orphanDependents', params['orphan_dependents']))
        if params.get('dry_run') is not None:
            query_params.append(('dryRun', params['dry_run']))
        if params.get('field_manager') is not None:
            query_params.append(('fieldManager', params['field_manager']))
        if params.get('force_conflicts') is not None:
            query_params.append(('force', params['force_conflicts']))
        if params.get('allow_watch_bookmarks') is not None:
            query_params.append(('allowWatchBookmarks', params['allow_watch_bookmarks']))

        header_params = params.get('header_params', {})
        form_params = []
        local_var_files = {}

        # Checking Accept header.
        new_header_params = dict((key.lower(), value) for key, value in header_params.items())
        if not 'accept' in new_header_params:
            header_params['Accept'] = self.client.select_header_accept([
                'application/json',
                'application/yaml',
            ])

        # HTTP header `Content-Type`
        if params.get('content_type'):
            header_params['Content-Type'] = params['content_type']
        else:
            header_params['Content-Type'] = self.client.select_header_content_type(['*/*'])

        # Authentication setting
        auth_settings = ['BearerToken']
        preload_content = 'response_type' in params and params['response_type'] is not None and params['response_type'] != ""

        api_response = self.client.call_api(
            path,
            method.upper(),
            path_params,
            query_params,
            header_params,
            body=body,
            post_params=form_params,
            async_req=params.get('async_req'),
            files=local_var_files,
            auth_settings=auth_settings,
            _preload_content=preload_content,
            _return_http_data_only=params.get('_return_http_data_only', True),
            _request_timeout=params.get('_request_timeout'),
            response_type=params.get('response_type', None)

        )
        if params.get('async_req'):
            return api_response.get()
        else:
            return api_response

    def parse(self, resource, data):
        if not isinstance(data, dict):
            data = data.to_dict()
        return self.client.deserialize(SimpleBody(json.dumps(data)),
                                       self.get_response_type(resource.group_version, resource.kind))
