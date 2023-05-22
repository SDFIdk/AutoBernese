"""
Module for dates.

"""
import datetime as dt
from dataclasses import dataclass
from typing import (
    Iterable,
    Protocol,
    Any,
)


class HasFromOrdinal(Protocol):
    """
    A formal definition of a type that can transform an ordinal date to what
    is needed.

    """
    def fromordinal(ordinal: int) -> Any:
        """
        Method that converts a Python integer date.

        """


def date_range(
    beg: dt.date | dt.datetime,
    end: dt.date | dt.datetime,
    /,
    *,
    transformer: HasFromOrdinal = dt.date,
) -> Iterable[Any]:
    """
    Return a range of dates between and including the given start and end dates.

    `datetime` instances are truncated to dates, since only `date` instances
    have the method `toordinal`.

    """
    if isinstance(beg, dt.datetime):
        beg = beg.date()
    if isinstance(end, dt.datetime):
        end = end.date()

    return [
        transformer.fromordinal(n)
        for n in range(
            beg.toordinal(),
            end.toordinal() + 1,
        )
    ]


def doy(d: dt.date | dt.datetime) -> int:
    """
    Day of year for a given date.

    """
    return d.timetuple().tm_yday


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


class GPSDate(dt.date):
    @classmethod
    def from_date(cls, date: dt.date | dt.datetime, /) -> "GPSDate":
        return cls(date.year, date.month, date.day)

    @classmethod
    def from_gps_week(cls, n: int | str, /) -> "GPSDate":
        date = date_from_gps_week(n)
        return cls(date.year, date.month, date.day)

    @classmethod
    def from_year_doy(cls, year: int | str, doy: int | str, /) -> "GPSDate":
        return cls(int(year), 1, 1) + dt.timedelta(int(doy) - 1)

    def date(self) -> dt.date:
        return dt.date(self.year, self.month, self.day)

    @property
    def gps_week(self) -> int:
        return gps_week(self)

    @property
    def doy(self) -> int:
        return doy(self)

    def dateinfo(self) -> dict[str, Any]:
        return dict(
            date=self.isoformat(),
            doy=self.doy,
            gps_week=self.gps_week,
            iso_week=self.isocalendar()[1],
            iso_weekday=self.isocalendar()[2],
        )
