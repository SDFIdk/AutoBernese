"""
Date handling and specific tools for conversion between different formats.

"""

import datetime as dt
from dataclasses import dataclass
from collections.abc import (
    Iterable,
)
from typing import (
    Protocol,
    Any,
)


def date_range(
    beg: dt.date | dt.datetime,
    end: dt.date | dt.datetime,
    /,
    *,
    extend_end_by: int = 0,
) -> Iterable[dt.date]:
    """
    By default, returns a range of dates between and including the given start
    and end dates.

    Note: `datetime` instances are truncated to dates, since only `date` instances
    have the method `toordinal`.

    """
    if isinstance(beg, dt.datetime):
        beg = beg.date()
    if isinstance(end, dt.datetime):
        end = end.date()
    if extend_end_by < 0:
        raise ValueError(f"{extend_end_by=}, but must be zero or greater.")

    return [
        dt.date.fromordinal(n)
        for n in range(
            beg.toordinal(),
            end.toordinal() + 1 + extend_end_by,
        )
    ]


def doy(d: dt.date | dt.datetime) -> int:
    """
    Day of year for a given date.

    """
    return d.timetuple().tm_yday


def doy2date(year: int, doy: int) -> dt.date:
    """
    Date from year and day-of-year

    """
    return dt.date(year, 1, 1) + dt.timedelta(days=doy - 1)


GPS_EPOCH = dt.date(1980, 1, 6)
"First GPS week"


def gps_week(date: dt.date | dt.datetime) -> int:
    """
    Calculate GPS-week number for given date.

    """
    if isinstance(date, dt.datetime):
        date = date.date()

    if date < GPS_EPOCH:
        raise ValueError("Date must be on or after first GPS week. Got {date!r} ...")

    return (date - GPS_EPOCH).days // 7


def gps_weekday(date: dt.date | dt.datetime) -> int:
    """
    Return given date's weekday number (zero-based) in GPS date.

    Python date and datetime instances count from Monday starint at zero.

    GPS weeks begin on Sundays and start at zero.

    Thus, the weekday number for GPS is Python date instance + 1 modulus 7.

    """
    return (date.weekday() + 1) % 7


def date_from_gps_week(gps_week: str | int) -> dt.date:
    return GPS_EPOCH + dt.timedelta(7 * int(gps_week))


class GPSDate(dt.datetime):
    """
    A GPSDate instance is a Python datetime instance with additional properties
    and a serialiser of particular data for that date or datetime.

    Both Python date and datetime instances can be wrapped.

    Note: Timezone data are not preserved.

    """

    @classmethod
    def from_date(cls, date: dt.date | dt.datetime, /) -> "GPSDate":
        """
        Create a GPSDate instance from an existing Python date or datetime
        instance.

        """
        if isinstance(date, dt.datetime):
            return cls(
                date.year, date.month, date.day, date.hour, date.minute, date.second
            )
        # It is a date instance without time, so we use midnight as the time
        return cls(date.year, date.month, date.day)

    @classmethod
    def from_gps_week(cls, gps_week: int | str, /) -> "GPSDate":
        return cls.from_date(date_from_gps_week(gps_week))

    @classmethod
    def from_year_doy(cls, year: int | str, doy: int | str, /) -> "GPSDate":
        return cls.from_date(doy2date(int(year), int(doy)))

    def date(self) -> dt.date:
        return dt.date(self.year, self.month, self.day)

    def datetime(self) -> dt.datetime:
        return dt.datetime(
            self.year, self.month, self.day, self.hour, self.minute, self.second
        )

    @property
    def gps_week(self) -> int:
        return gps_week(self)

    @property
    def gps_weekday(self) -> int:
        return gps_weekday(self)

    @property
    def doy(self) -> int:
        return doy(self)

    @property
    def y(self) -> int:
        return int(self.strftime("%y"))

    @property
    def info(self) -> dict[str, Any]:
        gps_week_beg = self.from_gps_week(self.gps_week)
        gps_week_mid = gps_week_beg + dt.timedelta(days=3)
        gps_week_end = gps_week_beg + dt.timedelta(days=6)
        return dict(
            weekday=self.strftime("%A"),
            timestamp=self.isoformat()[:10],
            doy=self.doy,
            iso_week=self.isocalendar()[1],
            iso_weekday=self.isocalendar()[2],
            gps_week=self.gps_week,
            gps_weekday=self.gps_weekday,
            # GPS week corresponds to a specific date without timestamp.
            gps_week_beg=gps_week_beg.isoformat()[:10],
            gps_week_mid=gps_week_mid.isoformat()[:10],
            gps_week_end=gps_week_end.isoformat()[:10],
        )


def dates_to_gps_date(dates: Iterable[dt.date]) -> list[GPSDate]:
    return [GPSDate.from_date(date) for date in dates]
