

class FieldErrorType(object):
    ErrorTypeNotFound = "FieldValueNotFound"
    ErrorTypeRequired = "FieldValueRequired"
    ErrorTypeDuplicate = "FieldValueDuplicate"
    ErrorTypeInvalid = "FieldValueInvalid"
    ErrorTypeNotSupported = "FieldValueNotSupported"
    ErrorTypeForbidden = "FieldValueForbidden"
    ErrorTypeTooLong = "FieldValueTooLong"
    ErrorTypeTooMany = "FieldValueTooMany"
    ErrorTypeInternal = "InternalError"
    ErrorTypeTypeInvalid = "FieldValueTypeInvalid"


OmitValue = "__omit__"


class FieldError(Exception):

    def __init__(self, _type, field, bad_value=OmitValue, detail=""):
        self.type = _type
        self.field = field
        self.bad_value = bad_value
        self.detail = detail

    def error_body(self):
        res = ""
        if self.type in {FieldErrorType.ErrorTypeRequired,
                         FieldErrorType.ErrorTypeForbidden,
                         FieldErrorType.ErrorTypeTooLong,
                         FieldErrorType.ErrorTypeInternal} or self.bad_value == OmitValue:
            res = self.type
        else:
            res = "{}: {}".format(self.type, str(self.bad_value))
        if len(self.detail) > 0:
            res += ": {}".format(self.detail)
        return res

    def __repr__(self):
        return "{}:{}".format(self.field, self.error_body())

    def __str__(self):
        return self.__repr__()


class Path(object):

    def __init__(self, name="", index="", parent=None):
        self.name = name
        self.parent = parent
        self._index = index

    def root(self):
        p = self
        while p.parent is not None:
            p = p.parent
        return p

    def child(self, name, *more_names):
        r = new_path(name, *more_names)
        r.root().parent = self
        return r

    def index(self, index: int):
        return Path(index=str(index), parent=self)

    def key(self, key: str):
        return Path(index=key, parent=self)

    def __repr__(self):
        if not self:
            return "<nil>"
        elems = []
        p = self
        while p is not None:
            elems.append(p)
            p = p.parent
        res = ""
        for i in range(len(elems)):
            p = elems[len(elems)-1-i]
            if p.parent is not None and len(p.name) > 0:
                res += "."
            if len(p.name) > 0:
                res += p.name
            else:
                res += "[%s]" % p.index
        return res

    def __str__(self):
        return self.__repr__()


def new_path(name: str, *more_names) -> Path:
    r = Path(name=name)
    for another_name in more_names:
        r = Path(name=another_name, parent=r)
    return r


class _PathOptions(object):

    def __init__(self, path: Path = None):
        self.path = path


def to_path(opts) -> Path:
    c = _PathOptions()
    for opt in opts:
        opt(c)
    if c.path is None:
        c.path = Path()
    return c.path


def invalid(field: Path, value, detail) -> FieldError:
    return FieldError(FieldErrorType.ErrorTypeTypeInvalid, str(field), value, detail)


def duplicate(field: Path, value) -> FieldError:
    return FieldError(FieldErrorType.ErrorTypeDuplicate, str(field), value)


def not_supported(field: Path, value, valid_values: list) -> FieldError:
    detail = ""
    if len(valid_values) > 0:
        quoted_values = [str(v) for v in valid_values]
        detail = "supported values: " + ", ".join(quoted_values)
    return FieldError(FieldErrorType.ErrorTypeNotSupported, str(field), value, detail)
