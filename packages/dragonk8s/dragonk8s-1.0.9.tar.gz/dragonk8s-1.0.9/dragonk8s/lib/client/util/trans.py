import copy

import json
import re
from kubernetes.client.models.v1_status import V1Status
from kubernetes.client.models.v1_status_details import V1StatusDetails
from kubernetes.client.models.v1_list_meta import V1ListMeta
from kubernetes.client.models.v1_status_cause import V1StatusCause
from kubernetes.client.api_client import ApiClient

Attribute2Obj = {
    "V1Status": V1Status(),
    "V1StatusDetails": V1StatusDetails(),
    "V1ListMeta": V1ListMeta(),
    "V1StatusCause": V1StatusCause(),
}

client = ApiClient()

class Resp(object):

    def __init__(self, data):
        self.data = data

def turn_param_style(params: dict):
    """
    将参数名的驼峰形式转为下划线形式
    @param params:
    @return:
    """
    temp_dict = {}
    for name, value in params.items():
        temp_name = ""
        if re.search("[A-Z]", name):
            capital_letters = re.findall("[A-Z]", name)
            for c in capital_letters:
                lower_c = c.lower()
                r_str = "_" + lower_c
                temp_name = name.replace(c, r_str)
        else:
            temp_name = name

        temp_dict.update({temp_name: value})

    return temp_dict


def _json_to_py_object(data, obj):
    """
    将json格式的数据转成python中k8s的对象
    :param data:
    :param obj:
    :return:
    """
    obj_copy = obj
    if data is None:
        return obj_copy
    if isinstance(data, dict):
        data_dict = data
    elif isinstance(data, str):
        data_dict = json.loads(data)
    else:
        return obj_copy
    att_map_reverse = {v: k for k, v in getattr(obj_copy, "attribute_map").items()}
    for k, v in data_dict.items():
        if k not in att_map_reverse:
            continue
        py_k = att_map_reverse[k]
        my_type = getattr(obj_copy, "openapi_types")[py_k]
        patt = "list\[(.*)\]"
        is_list = False
        m = re.match(patt, my_type)
        if m is not None and len(m.group())> 1:
            is_list = True
            my_type = m.groups([0])
        if my_type in {"str", "int", "datetime"}:
            setattr(obj_copy, py_k, v)
            continue
        if is_list:
            setattr(obj_copy, py_k, json_to_py_object_list(v, get_simple_obj_by_name(my_type)))
        else:
            setattr(obj_copy, py_k, _json_to_py_object(v, get_simple_obj_by_name(my_type)))

    return obj_copy


def json_to_py_object_list(data, obj):
    """
    将json格式的数据转成python中k8s的对象
    :param data:
    :param obj:
    :return:
    """
    if data is None:
        return []
    if isinstance(data, list):
        data_list = data
    else:
        data_list = json.loads(data)

    res = []
    for d in data_list:
        res.append(_json_to_py_object(d, obj))
    return res


def parse_v1_status(data: str) -> V1Status:
    status = V1Status()
    _json_to_py_object(data, status)
    status.details = _json_to_py_object(status.details, V1StatusDetails())
    status.metadata = _json_to_py_object(status.metadata, V1ListMeta())
    status.details.causes = json_to_py_object_list(status.details.causes, V1StatusCause())
    return status


def get_simple_obj_by_name(name: str):
    if name in Attribute2Obj:
        return copy.deepcopy(Attribute2Obj[name])
    raise Exception("%s is not in Attribute2Obj cache" % name)


def parse_json_to_object(data: str, obj):
    if isinstance(obj, str):
        obj = get_simple_obj_by_name(obj)
    return _json_to_py_object(data, obj)


def parse_json_to_object_by_class_name(data: str, obj_type):
    return client.deserialize(Resp(data), obj_type)
