import datetime as dt
from pathlib import Path

from ab import configuration
from ab.vmf import _input_filepaths


def test_input_filenames():
    path = Path("{date.year}")
    date = dt.date(2023, 1, 1)
    ifname = configuration.load().get("troposphere").get("ifname")
    result_list = _input_filepaths(path, ifname, date)
    expected_list = [
        Path("2023/VMF3_20230101.H00"),
        Path("2023/VMF3_20230101.H06"),
        Path("2023/VMF3_20230101.H12"),
        Path("2023/VMF3_20230101.H18"),
        Path("2023/VMF3_20230102.H00"),
    ]
    for result, expected in zip(result_list, expected_list):
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."
