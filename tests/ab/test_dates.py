import datetime as dt

from ab.dates import (
    date_range,
)


def test_date_range():
    t0 = dt.datetime(1997, 5, 1, 15, 30, 0)
    t1 = dt.datetime(1997, 5, 5, 0, 0, 0)
    expected_dates = (
        dt.date(1997, 5, 1),
        dt.date(1997, 5, 2),
        dt.date(1997, 5, 3),
        dt.date(1997, 5, 4),
        dt.date(1997, 5, 5),
    )
    resulting_dates = date_range(t0, t1)
    assert len(resulting_dates) == len(expected_dates), f"Length of resulting sequence is different from that of the expected sequence ..."

    for (result, expected) in zip(resulting_dates, expected_dates):
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."
