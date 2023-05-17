import datetime as dt
from typing import Iterable


def date_range(beg: dt.date | dt.datetime, end: dt.date | dt.datetime, /) -> Iterable[dt.date]:
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
        dt.date.fromordinal(n)
        for n in range(
            beg.toordinal(),
            end.toordinal() + 1,
        )
    ]
