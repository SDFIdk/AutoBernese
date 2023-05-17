import datetime as dt

import pytest

from ab.dates import (
    date_range,
    GPS_EPOCH,
    gps_week,
    date_from_gps_week,
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
    assert len(resulting_dates) == len(
        expected_dates
    ), f"Length of resulting sequence is different from that of the expected sequence ..."

    for result, expected in zip(resulting_dates, expected_dates):
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."


@pytest.mark.parametrize(
    "date, week",
    [
        # Date, GPS week
        (dt.date(1980, 1, 6), 0),
        (dt.date(1985, 7, 25), 289),
        (dt.date(1994, 2, 8), 735),
        (dt.date(2015, 10, 14), 1866),
        (dt.date(2022, 8, 11), 2222),
        (dt.date(2023, 2, 21), 2250),
    ],
)
def test_gps_week(date, week):
    print(f"{date=}: {week=}")
    assert gps_week(date) == week


def test_date_from_gps_week():
    expected = dt.date(1980, 1, 6)
    gps_week_for_gps_epoch = 0
    result = date_from_gps_week(gps_week_for_gps_epoch)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
