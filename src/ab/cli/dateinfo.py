"""
Command-line interface for date information

"""

import logging
from pathlib import Path
import json
import datetime as dt
from typing import (
    Any,
    Final,
)

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print

from ab import (
    dates,
)

from ab.cli import (
    _input,
    _arguments,
)


log = logging.getLogger(__name__)


@click.group(cls=ClickAliasedGroup)
def dateinfo() -> None:
    """
    Print date info on date, year+doy or GPS week.

    """


@dateinfo.command
@_arguments.date
def ymd(date: dt.date) -> None:
    """
    Show date information based on date.

    """
    gps_date = dates.GPSDate.from_date(date)
    print(json.dumps(gps_date.info, indent=2))


@dateinfo.command
@_arguments.week
def gpsweek(week: int) -> None:
    """
    Show date information based on GPS week.

    """
    gps_date = dates.GPSDate.from_gps_week(week)
    print(json.dumps(gps_date.info, indent=2))


@dateinfo.command
@_arguments.year
@_arguments.doy
def ydoy(year: int, doy: int) -> None:
    """
    Show date information based on Year and day of year [DOY].

    """
    gps_date = dates.GPSDate.from_year_doy(year, doy)
    print(json.dumps(gps_date.info, indent=2))
