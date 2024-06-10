import datetime as dt

from ab.vmf import (
    _input_filenames,
)


def test_input_filenames():
    date = dt.date(2023, 1, 1)
    result_list = _input_filenames(date)
    expected_list = [
        "2023/VMF3_20230101.H00",
        "2023/VMF3_20230101.H06",
        "2023/VMF3_20230101.H12",
        "2023/VMF3_20230101.H18",
        "2023/VMF3_20230102.H00",
    ]
    for result, expected in zip(result_list, expected_list):
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."
