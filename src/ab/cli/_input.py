"""
Command-line types

"""

from typing import Final
import datetime as dt


DATE_FORMAT: Final = "%Y-%m-%d"


def date(s: str) -> dt.date:
    return dt.datetime.strptime(s, DATE_FORMAT).date()


def prompt_proceed() -> bool:
    return input("Proceed? (y/[n]): ").lower() == "y"
