import json
from dragonk8s.lib.client.util.trans import parse_json_to_object_by_class_name
from dragonk8s.dragon.exceptions import ApiException
from kubernetes.client.models import V1StatusCause, V1Status, V1StatusDetails
from dragonk8s.lib.apimachinery.pkg.apis import meta_v1

def reason_for_error(ex) -> str:
    if ex is not None and ex.body is not None:
        try:
            status = json.loads(ex.body)
        except:
            return 'unknow'
        else:
            if 'reason' in status:
                return status['reason']
    return 'unknow'


def is_already_exists(ex) -> bool:
    return reason_for_error(ex) == 'AlreadyExists'


CauseTypeFieldValueNotFound = "FieldValueNotFound"
CauseTypeFieldValueRequired = "FieldValueRequired"
CauseTypeFieldValueDuplicate  = "FieldValueDuplicate"
CauseTypeFieldValueInvalid = "FieldValueInvalid"
CauseTypeFieldValueNotSupported = "FieldValueNotSupported"
CauseTypeUnexpectedServerResponse = "UnexpectedServerResponse"
CauseTypeFieldManagerConflict = "FieldManagerConflict"
CauseTypeResourceVersionTooLarge = "ResourceVersionTooLarge"
NamespaceTerminatingCause  = "NamespaceTerminating"


StatusReasonUnknown = ""
StatusReasonUnauthorized = "Unauthorized"
StatusReasonForbidden = "Forbidden"
StatusReasonNotFound = "NotFound"
StatusReasonAlreadyExists = "AlreadyExists"
StatusReasonConflict = "Conflict"
StatusReasonGone = "Gone"
StatusReasonInvalid = "Invalid"
StatusReasonServerTimeout = "ServerTimeout"
StatusReasonTimeout = "Timeout"
StatusReasonTooManyRequests = "TooManyRequests"
StatusReasonBadRequest = "BadRequest"
StatusReasonMethodNotAllowed = "MethodNotAllowed"
StatusReasonNotAcceptable = "NotAcceptable"
StatusReasonRequestEntityTooLarge = "RequestEntityTooLarge"
StatusReasonUnsupportedMediaType = "UnsupportedMediaType"
StatusReasonInternalError = "InternalError"
StatusReasonExpired = "Expired"
StatusReasonServiceUnavailable = "ServiceUnavailable"


known_reason = {StatusReasonUnauthorized, StatusReasonForbidden, StatusReasonNotFound, StatusReasonAlreadyExists,
                StatusReasonConflict, StatusReasonGone, StatusReasonInvalid, StatusReasonServerTimeout,
                StatusReasonTimeout, StatusReasonTooManyRequests, StatusReasonBadRequest, StatusReasonMethodNotAllowed,
                StatusReasonNotAcceptable, StatusReasonRequestEntityTooLarge, StatusReasonUnsupportedMediaType,
                StatusReasonInternalError, StatusReasonExpired, StatusReasonServiceUnavailable}


def status_cause(e: ApiException, cause_name: str) -> (V1StatusCause, bool):
    if not hasattr(e, "body"):
        return V1StatusCause(), False
    body = e.body
    status = parse_json_to_object_by_class_name(body, "V1Status")
    if not status.details or not status.details.causes:
        return V1StatusCause(), False
    for cause in status.details.causes:
        if cause.reason == cause_name:
            return cause, True
    return V1StatusCause(), False


def has_status_cause(e: ApiException, cause_name: str) -> bool:
    _, ok = status_cause(e, cause_name)
    return ok


def _reason_and_code_for_error(e: ApiException) -> (str, int):
    if not hasattr(e, "body"):
        return StatusReasonUnknown, 0
    body = e.body
    status = parse_json_to_object_by_class_name(body, "V1Status")
    return status.reason, status.code


def is_not_found(e: ApiException) -> bool:
    reason, code = _reason_and_code_for_error(e)
    if reason == StatusReasonNotFound:
        return True
    if reason in known_reason:
        return code == 404
    return False


def is_invalid(e: ApiException) -> bool:
    reason, code = _reason_and_code_for_error(e)
    if reason == StatusReasonInvalid:
        return True
    if reason not in known_reason and code == 422:
        return True
    return False

def is_resource_expired(e: ApiException) -> bool:
    return reason_for_error(e) == StatusReasonExpired


def is_timeout(e: ApiException) -> bool:
    reason, code = _reason_and_code_for_error(e)
    if reason == StatusReasonTimeout:
        return True
    if reason not in known_reason and code == 504:
        return True
    return False


def is_too_large_resource_version_error(e: ApiException) -> bool:
    if has_status_cause(e, CauseTypeResourceVersionTooLarge):
        return True
    if not is_timeout(e):
        return False
    if not hasattr(e, "body"):
        return False
    body = e.body
    status = parse_json_to_object_by_class_name(body, "V1Status")
    if not status.details or not status.details.causes:
        return False
    for cause in status.details.causes:
        if cause.message == "Too large resource version":
            return True
    return False


def is_too_many_requests(e: ApiException) -> bool:
    reason, code = _reason_and_code_for_error(e)
    if reason == StatusReasonTooManyRequests:
        return True
    if code == 429:
        return True
    return False


def new_not_found(gvk, name: str) -> ApiException:
    status = V1Status(
        status=meta_v1.StatusFailure,
        code=404,
        reason=StatusReasonNotFound,
        details=V1StatusDetails(
            group=gvk.group,
            kind=gvk.kind,
            name=name,
        ),
    )
    res = ApiException(status=meta_v1.StatusFailure, reason=StatusReasonNotFound)
    res.body = json.dumps(status.to_dict())
    return res
