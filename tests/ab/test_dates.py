import datetime as dt

import pytest

from ab.dates import (
    date_range,
    doy,
    doy2date,
    GPS_EPOCH,
    gps_week,
    gps_weekday,
    date_from_gps_week,
    GPSDate,
)


def test_date_range_simple():
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


def test_date_range_extended_end():
    t0 = dt.datetime(1997, 5, 1)
    t1 = dt.datetime(1997, 5, 3)
    extend_end_by = 1
    expected_dates = (
        dt.date(1997, 5, 1),
        dt.date(1997, 5, 2),
        dt.date(1997, 5, 3),
        dt.date(1997, 5, 4),
    )
    resulting_dates = date_range(t0, t1, extend_end_by=extend_end_by)
    assert len(resulting_dates) == len(
        expected_dates
    ), f"Length of resulting sequence is different from that of the expected sequence ..."

    for result, expected in zip(resulting_dates, expected_dates):
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_doy():
    test_data = (
        (dt.date(1990, 1, 1), 1),
        (dt.date(2025, 6, 2), 153),
    )
    for date, expected in test_data:
        result = doy(date)
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_doy2date():
    test_data = (
        ((1990, 1), dt.date(1990, 1, 1)),
        ((2025, 153), dt.date(2025, 6, 2)),
    )
    for (year, doy_), expected in test_data:
        result = doy2date(year, doy_)
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_gps_week():
    test_data = (
        # Date, GPS week
        (dt.date(1980, 1, 6), 0),
        (dt.date(1985, 7, 25), 289),
        (dt.date(1994, 2, 8), 735),
        (dt.date(2015, 10, 14), 1866),
        (dt.date(2022, 8, 11), 2222),
        (dt.date(2023, 2, 21), 2250),
    )
    for date, expected in test_data:
        result = gps_week(date)
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_gps_weekday():
    test_data = (
        (dt.date(2023, 10, 28), 6),
        (dt.date(2023, 10, 29), 0),
        (dt.date(2023, 10, 30), 1),
        (dt.date(2023, 10, 31), 2),
        (dt.date(2023, 11, 1), 3),
        (dt.date(2023, 11, 2), 4),
        (dt.date(2023, 11, 3), 5),
        (dt.date(2023, 11, 4), 6),
        (dt.date(2023, 11, 5), 0),
        (dt.date(2023, 11, 6), 1),
        (dt.date(2023, 11, 7), 2),
    )
    for date, expected in test_data:
        result = gps_weekday(date)
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_date_from_gps_week():
    expected = dt.date(1980, 1, 6)
    gps_week_for_gps_epoch = 0
    result = date_from_gps_week(gps_week_for_gps_epoch)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_GPSDate_two_digit_year():
    date = GPSDate(1980, 1, 6)
    expected = 80
    result = date.y
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
