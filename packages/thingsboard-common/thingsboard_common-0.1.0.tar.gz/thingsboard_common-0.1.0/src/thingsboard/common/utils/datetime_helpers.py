# -*- coding: utf-8 -*-

import datetime

EPOCH = datetime.datetime.fromtimestamp(0, datetime.UTC)


def get_current_timestamp() -> int:
    """Creates a timestamp using the current date and time.

    The timestamp returned is in milliseconds.
    """
    current_date_time = datetime.datetime.now(datetime.UTC)
    return _unix_time_millis(current_date_time)


def get_timestamp(dt: datetime.datetime) -> int:
    """Creates a timestamp using parameter dt.
    :param dt The datetime object to convert to a timestamp
    """
    return _unix_time_millis(dt)


def _unix_time_millis(dt: datetime.datetime) -> int:
    """Converts a datetime object into unix time including milliseconds.
    :param dt The datetime object to convert.
    """
    ut = int((dt - EPOCH).total_seconds()) * 1000
    ut += int(dt.microsecond / 1000)
    return ut
