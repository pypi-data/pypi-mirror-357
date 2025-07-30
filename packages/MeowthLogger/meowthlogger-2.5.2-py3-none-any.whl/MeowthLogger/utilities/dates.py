import re
from datetime import datetime, timedelta

from MeowthLogger.constants import (
    LOGSTRING_DATE_FORMAT,
    LOGSTRING_DATE_REGEXP,
    REQUEST_DATESTRING_FORMAT,
)
from MeowthLogger.errors import NotDateLogString, NotValidLogsDateFormat


def convert_request_datestring(request_date_string: str) -> datetime:
    """Converting reques string date to datetime object"""
    try:
        d = datetime.strptime(request_date_string, REQUEST_DATESTRING_FORMAT)
        return d
    except:
        raise NotValidLogsDateFormat


def set_null_minutes(date: datetime) -> datetime:
    """Preparing date for get datetime hour object"""
    return date - timedelta(
        minutes=date.minute, seconds=date.second, microseconds=date.microsecond
    )


def date_from_logstring(log_string: str) -> datetime:
    """Preparing date in logstring date format to datetime object"""
    date_pattern = re.compile(LOGSTRING_DATE_REGEXP)
    match = date_pattern.search(log_string)

    if not match:
        raise NotDateLogString

    return datetime.strptime(match.group(1), LOGSTRING_DATE_FORMAT)
