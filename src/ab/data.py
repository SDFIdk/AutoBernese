"""
Module for downloading source data

"""
from datetime import date, timedelta


def calc_gps_week(tocalc: date) -> int:
    """Calculates the GPS week number for a given date"""
    gps_epoch = date(1980, 1, 6)  # first GPS week
    epoch_monday = gps_epoch - timedelta(gps_epoch.weekday())
    today_monday = tocalc - timedelta(tocalc.weekday())
    return int((today_monday - epoch_monday).days / 7)


def download_sources() -> None:
    print("Downloading A")
    print("Downloading B")
    print("Downloading C")
    print("Downloading D")
    print("Downloading .")
    print("Downloading .")
    print("Downloading .")
    print("Finished")
