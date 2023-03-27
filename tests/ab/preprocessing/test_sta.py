import datetime as dt

from ab.preprocessing.sta import (
    STA_created_timestamp,
)


def test_STA_created_timestamp():
    d = dt.datetime(2023, 3, 15, 13, 50)
    expected = '15-MAR-23 13:50'
    result = STA_created_timestamp(d)
    assert result == expected, f'Expected {result!r} to be {expected!r} ...'
