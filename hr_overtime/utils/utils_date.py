import pytz
from pytz import timezone

import logging

_logger = logging.getLogger(__name__)


def timestamp_to_utc(timestamp, tz):
    ts_with_tz = timezone(tz).localize(timestamp)
    ts_utc = ts_with_tz.astimezone(pytz.utc)
    return ts_utc.strftime("%Y-%m-%d %H:%M:%S")


def utc_to_timestamp(ts, tz):
    return timezone(tz).normalize(pytz.utc.localize(ts))
