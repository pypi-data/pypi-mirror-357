import copy
import logging

from dragonk8s.lib.apimachinery.pkg import selection
from dragonk8s.lib.apimachinery.pkg.util.validation import field
from dragonk8s.lib.apimachinery.pkg.util import validation
from dragonk8s.lib.apimachinery.pkg.selection import Operator
from dragonk8s.lib.util import string

_unary_operators = [Operator.Exists, Operator.DoesNotExist]
_binary_operators = [Operator.In, Operator.NotIn, Operator.Equals, Operator.DoubleEquals, Operator.NotEquals,
                     Operator.GreaterThan, Operator.LessThan]
valid_requirement_operators = copy.copy(_unary_operators)
valid_requirement_operators.extend(_binary_operators)


class Labels(object):

    def has(self, label: str) -> bool:
        pass

    def get(self, label: str) -> str:
        pass


def _validate_label_key(k: str, path: field.Path):
    try:
        validation.is_qualified_name(k)
    except Exception as e:
        raise field.invalid(path, k, str(e))


def _validate_label_value(k, v, path: field.Path):
    try:
        validation.is_valid_label_value(v)
    except Exception as e:
        raise field.invalid(path.key(k), v, str(e))


class Requirement(object):

    def __init__(self, key: str, op: str, vals: list):
        self.key = key
        self.operator = op
        self.str_values = vals

    def has_value(self, value: str) -> bool:
        return value in self.str_values

    def matches(self, ls: Labels):
        if self.operator in {Operator.In, Operator.Equals, Operator.DoubleEquals}:
            if not ls.has(self.key):
                return False
            return self.has_value(ls.get(self.key))
        elif self.operator in {Operator.NotIn, Operator.NotEquals}:
            if not ls.has(self.key):
                return True
            return not self.has_value(ls.get(self.key))
        elif self.operator == Operator.Exists:
            return ls.has(self.key)
        elif self.operator == Operator.DoesNotExist:
            return not ls.has(self.key)
        elif self.operator in {Operator.GreaterThan, Operator.LessThan}:
            if not ls.has(self.key):
                return False
            try:
                ls_value = int(ls.get(self.key))
            except Exception as e:
                logging.warning("parse failed for value: %s in label %s: %s", str(ls.get(self.key)), ls, str(e))
                return False
            if len(self.str_values) != 1:
                logging.warning("Invalid value count %s of requirement %s, "
                                "for 'Gt', 'Lt' operators, exactly one value is required", len(self.str_values), self)
                return False
            for v in self.str_values:
                try:
                    self_v = int(v)
                except Exception as e:
                    logging.warning("parse failed for value %s in requirement %s,"
                                    " for 'Gt', 'Lt' operators, the value must be an integer", v, self)
                    return False
            if self.operator == Operator.GreaterThan:
                return ls_value > self_v
            elif self.operator == Operator.LessThan:
                return ls_value < self_v
        else:
            return False

    def __repr__(self):
        res = ""
        if self.operator == Operator.DoesNotExist:
            res += "!"
        res += self.key
        if self.operator == Operator.Equals:
            res += "="
        elif self.operator == Operator.DoubleEquals:
            res += "=="
        elif self.operator == Operator.NotEquals:
            res += "!="
        elif self.operator == Operator.In:
            res += " in "
        elif self.operator == Operator.NotIn:
            res += " notin "
        elif self.operator == Operator.GreaterThan:
            res += ">"
        elif self.operator == Operator.LessThan:
            res += "<"
        elif self.operator in {Operator.Exists, Operator.DoesNotExist}:
            return res

        if self.operator in {Operator.In, Operator.NotIn}:
            res += "("
        if len(self.str_values) == 1:
            res += self.str_values[0]
        else:
            res += ", ".join(self.str_values)
        if self.operator in {Operator.In, Operator.NotIn}:
            res += ")"
        return res

    def __str__(self):
        return self.__repr__()

    @property
    def values(self):
        return self.str_values

    def __eq__(self, other):
        if self.key != other.key:
            return False
        if self.operator != other.operator:
            return False
        return string.list_equal(self.str_values, other.str_values)


def new_requirement(key: str, op: str, vals: list, *opts):
    path = field.to_path(opts)
    _validate_label_key(key, path.child("key"))

    value_path = path.child("values")
    if op in {Operator.In, Operator.NotIn}:
        if len(vals) == 0:
            raise field.invalid(value_path, vals, "for 'in', 'not in' operators, values set can't be empty")
    elif op in {Operator.In, Operator.DoubleEquals, Operator.NotEquals}:
        if len(vals) != 1:
            raise field.invalid(value_path, vals, "exact-match compatibility requires on single value")
    elif op in {Operator.Exists, Operator.DoesNotExist}:
        if len(vals) != 0:
            raise field.invalid(value_path, vals, "values set must be empty for exists and does not exist")
    elif op in {Operator.GreaterThan, Operator.LessThan}:
        if len(vals) != 1:
            raise field.invalid(value_path, vals, "for 'Gt', 'Lt' operators, exactly one value is required")
        for i in range(len(vals)):
            try:
                int(vals[i])
            except:
                raise field.invalid(value_path.index(i), vals[i],
                                    "for 'Gt', 'Lt' operators, the value mutst be an interger")
    else:
        raise field.not_supported(path.child("operator"), op, valid_requirement_operators)
    for i in range(len(vals)):
        _validate_label_value(key, vals[i], value_path.index(i))

    return Requirement(key=key, op=op, vals=vals)


class Set(Labels):

    def __init__(self, data=None):
        self._data = {} if not data else data

    def __repr__(self):
        selector = []
        for k, v in self._data.items():
            selector.append("{}={}".format(k, v))
        return ",".join(selector)

    def __str__(self):
        return self.__repr__()

    def has(self, label: str) -> bool:
        return label in self._data

    def get(self, label: str) -> str:
        return self._data[label] if label in self._data else None


class Selector(object):

    def matches(self, labels: Labels) -> bool:
        pass

    def empty(self) -> bool:
        pass

    def add(self, *r: Requirement):
        pass

    def requirements(self) -> (list, bool):
        pass

    def requires_exact_match(self, label: str) -> (str, bool):
        pass


class _InternalSelector(Selector):

    def __init__(self, data=None):
        if not data:
            self._data = []
        else:
            self._data = data

    def matches(self, labels: Labels) -> bool:
        for r in self._data:
            if not r.matches(labels):
                return False
        return True

    def empty(self) -> bool:
        return len(self._data) == 0

    def add(self, *r: Requirement):
        self._data.extend(r)
        # todo sort
        return self

    def requirements(self) -> (list, bool):
        return self._data, True

    def requires_exact_match(self, label: str) -> (str, bool):
        for r in self._data:
            if r.key == label:
                if r.operator in {Operator.Equals, Operator.DoubleEquals, Operator.In}:
                    if len(r.str_values) == 1:
                        return r.str_values[0], True
                return "", False
        return "", False

    def __repr__(self):
        res = []
        for s in self._data:
            res.append(str(s))
        return ",".join(res)

    def __str__(self):
        return self.__repr__()


class _NothingSelector(Selector):
    def matches(self, labels: Labels) -> bool:
        return False

    def empty(self) -> bool:
        return False

    def add(self, *r: Requirement):
        pass

    def requirements(self) -> (list, bool):
        return [], False

    def requires_exact_match(self, label: str) -> (str, bool):
        return "", False

    def __repr__(self):
        return ""

    def __str__(self):
        return ""


def selector_from_validated_set(ls: Set) -> Selector:
    if ls is None or len(ls._data) == 0:
        return _InternalSelector()
    reqs = []
    for k, v in ls._data.items():
        reqs.append(Requirement(key=k, op=Operator.Equals, vals=[v]))
    return _InternalSelector(data=reqs)


def selector_from_set(ls: Set) -> Selector:
    return selector_from_validated_set(ls)


every_thing = _InternalSelector()
nothing = _NothingSelector()

def new_selector() -> Selector:
    return _InternalSelector()