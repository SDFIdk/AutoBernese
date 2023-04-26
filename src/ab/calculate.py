import datetime as dt


GPS_EPOCH = dt.date(1980, 1, 6)
"First GPS week"


def gps_week(date: dt.date | dt.datetime) -> int:
    """
    Calculate GPS-week number for given date.

    """
    if date < GPS_EPOCH:
        raise ValueError("Date must be on or after first GPS week. Got {date!r} ...")
    return (date - GPS_EPOCH).days // 7
