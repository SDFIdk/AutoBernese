"""
Tests for the ab.data module
"""
import datetime as dt

import pytest

from ab.data import calc_gps_week


@pytest.mark.parametrize(
    "date, gps_week",
    [
        # Date, GPS week
        (dt.date(1980, 1, 6), 0),
        (dt.date(1985, 7, 25), 289),
        (dt.date(1994, 2, 8), 735),
        (dt.date(2015, 10, 14), 1866),
        (dt.date(2023, 2, 21), 2250),
    ],
)
def test_calc_gps_week(date, gps_week):
    print(f"{date=}: {gps_week=}")
    assert calc_gps_week(date) == gps_week
