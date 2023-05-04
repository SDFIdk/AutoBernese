"""
Module for GPS dates.

"""
import datetime as dt
from dataclasses import dataclass


GPS_EPOCH = dt.date(1980, 1, 6)
"First GPS week"


def gps_week(date: dt.date | dt.datetime) -> int:
    """
    Calculate GPS-week number for given date.

    """
    if date < GPS_EPOCH:
        raise ValueError("Date must be on or after first GPS week. Got {date!r} ...")
    return (date - GPS_EPOCH).days // 7


def date_from_gps_week(gps_week: str | int) -> dt.date:
    return GPS_EPOCH + dt.timedelta(7 * int(gps_week))


@dataclass
class GPSWeek:
    week: int

    def __post_init__(self) -> None:
        self.week = int(self.week)

    def date(self) -> dt.date:
        return date_from_gps_week(self.week)
