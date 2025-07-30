from datetime import datetime
from pytz import utc


time_format = "%Y-%m-%dT%H:%M:%SZ"
time_format_ns = "%Y-%m-%dT%H:%M:%S.%fZ"


def _timestamp2str(t: float) -> str:
    return datetime.fromtimestamp(t).strftime(time_format)


def _datetime2str(t: datetime) -> str:
    return t.strftime(time_format)


def _timestamp2datetime(t: float) -> datetime:
    return datetime.fromtimestamp(t)


def to_time_str(t) -> str:
    if isinstance(t, str):
        return t
    if isinstance(t, float) or isinstance(t, int):
        return _timestamp2str(t)
    return _datetime2str(t)


def to_time_str_with_ns(t) -> str:
    if isinstance(t, datetime):
        t = t.timestamp()
    ns = t - float(int(t))
    tf = time_format_ns.format(ns)
    return datetime.fromtimestamp(t).astimezone(utc).strftime(tf)


def parse_time(t) -> float:
    if isinstance(t, float) or isinstance(t, int):
        return t
    if isinstance(t, str):
        return datetime.strptime(t, time_format).timestamp()
    return t.timestamp()
