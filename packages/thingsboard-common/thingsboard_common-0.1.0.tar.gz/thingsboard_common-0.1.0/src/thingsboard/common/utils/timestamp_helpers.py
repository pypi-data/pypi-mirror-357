# -*- coding: utf-8 -*-

import datetime

EPOCH = datetime.datetime.fromtimestamp(0, datetime.UTC)

def get_time_in_milliseconds(dt: datetime.datetime = None) -> int:
    """Creates a timestamp using the current date and time.

    If no parameters is given the actual UTC time is taken.
    """
    if not dt:
        dt = datetime.datetime.now(datetime.UTC)

    ut = int((dt - EPOCH).total_seconds()) * 1000
    ut += int(dt.microsecond / 1000)
    return ut
