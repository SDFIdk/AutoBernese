"""
Date handling and specific tools for conversion between different formats.

"""

import datetime as dt
from typing import (
    Any,
    Final,
)


END_INCLUDED: Final = 1
"Add this to `range` in `date_range` to include both start and end date in range."


def asdate(date: dt.datetime) -> dt.date:
    """
    Return a date instance from a datetime instance or the date itself, if the
    input is actually a date instance.

    Raises a TypeError, if the instance is neither a date or datetime instance.

    """
    # NOTE: The order of these checks is important, since `isinstance()` allows
    # for a datetime instance be an instance of date. We want to specifically
    # check for a datetime instance first, and then anything that derives from
    # the date type such as GPSDate will be interpreted as a date and be
    # returned without modification.
    if isinstance(date, dt.datetime):
        return date.date()
    if isinstance(date, dt.date):
        return date
    raise TypeError(f"Expected input date to be datetime instance. Got {date!r} ...")


def date_range(
    beg: dt.date | dt.datetime,
    end: dt.date | dt.datetime | None = None,
    /,
    *,
    extend_end_by: int = 0,
) -> list[dt.date]:
    """
    By default, returns a range of dates between and including the given start
    and end dates.

    Note: `datetime` instances are truncated to dates, since only `date` instances
    have the method `toordinal`.

    """
    # Range validation
    if extend_end_by < 0:
        raise ValueError(f"{extend_end_by=}, but must be zero or greater.")

    # Allowing end to be None to obtain today's date
    if end is None:
        end = beg

    # Casting (+ implicitly type validating), if needed, to date instances which
    # have the ordinal-properties.
    beg = asdate(beg)
    end = asdate(end)

    return [
        dt.date.fromordinal(n)
        for n in range(
            beg.toordinal(),
            end.toordinal() + END_INCLUDED + extend_end_by,
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
    date = asdate(date)
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


def date_from_gps_week(gps_week: int | str) -> dt.date:
    return GPS_EPOCH + dt.timedelta(7 * int(gps_week))


def gps_week_limits(gps_week: int | str) -> tuple[dt.date, dt.date]:
    beg = date_from_gps_week(gps_week)
    end = beg + dt.timedelta(days=6)
    return (beg, end)


def gps_week_range(gps_week: int | str) -> list[dt.date]:
    return date_range(*gps_week_limits(gps_week))


class GPSDate(dt.date):
    """
    A GPSDate instance is a Python datetime instance with additional properties
    and a serialiser of particular data for that date or datetime.

    Both Python date and datetime instances can be wrapped.

    Note: Timezone data are not preserved.

    """

    @classmethod
    def from_date(cls, date: dt.date | dt.datetime, /) -> "GPSDate":
        """
        Create a GPSDate instance from an existing date instance.

        """
        date = asdate(date)
        return cls(date.year, date.month, date.day)

    @classmethod
    def from_gps_week(cls, gps_week: int | str, /) -> "GPSDate":
        """
        Create a GPSDate instance from a valid GPS week.

        """
        return cls.from_date(date_from_gps_week(gps_week))

    @classmethod
    def from_year_doy(cls, year: int | str, doy: int | str, /) -> "GPSDate":
        """
        Create a GPSDate instance from a valid day-of-year.

        """
        return cls.from_date(doy2date(int(year), int(doy)))

    def date(self) -> dt.date:
        """
        Return date as Python date instance.

        """
        return dt.date(self.year, self.month, self.day)

    @property
    def gps_week(self) -> int:
        """
        Return GPS week number for date.

        """
        return gps_week(self)

    @property
    def gps_weekday(self) -> int:
        """
        Return weekday index for GPS week (Sunday is 0).

        """
        return gps_weekday(self)

    @property
    def doy(self) -> int:
        """
        Return day-of-year count of the date's year.

        """
        return doy(self)

    @property
    def y(self) -> int:
        """
        Return two-digit year as integer.

        """
        return int(self.strftime("%y"))

    @property
    def info(self) -> dict[str, Any]:
        """
        Return instance information in serialisable form.

        """
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


def dates_to_gps_date(dates: list[dt.date]) -> list[GPSDate]:
    return [GPSDate.from_date(date) for date in dates]
