"""
Module for probing local files.

"""
import datetime as dt
from typing import (
    Any,
    Iterable,
)
import math
from pathlib import Path

import logging


log = logging.getLogger(__name__)


# Local files
def date_changed(fname: Path | str) -> dt.date:
    raw = Path(fname).stat().st_ctime
    return dt.datetime.fromtimestamp(raw).date()


def file_age(fname: Path) -> int:
    """
    Returns age of file in days since today.

    """
    return (dt.date.today() - date_changed(fname)).days


def already_downloaded(fname: Path, *, max_age: int | float = math.inf) -> bool:
    """
    A file is already downloaded if it exists, and it is newer than the given
    maximum age.

    """
    return fname.is_file() and file_age(fname) < max_age
