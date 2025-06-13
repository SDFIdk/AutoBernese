"""
Probe local files.

"""

import os
import datetime as dt
from typing import (
    Any,
    Iterable,
)
import math
from pathlib import Path
import functools

import logging


log = logging.getLogger(__name__)


def date_changed(fname: Path | str) -> dt.date:
    """
    Return the last modification date for given file.

    """
    fname = Path(fname)
    if not fname.is_file():
        raise ValueError(f"File {fname!r} does not exist ...")
    return dt.datetime.fromtimestamp(fname.stat().st_ctime).date()


def file_age(fname: Path) -> int:
    """
    Returns age of file in days since today.

    """
    return (dt.date.today() - date_changed(fname)).days


def already_updated(fname: Path, *, max_age: int | float = math.inf) -> bool:
    """
    A file is already updated if it exists, and it is newer than the given
    maximum age.

    """
    return fname.is_file() and file_age(fname) < max_age


@functools.cache
def dir_size(start_path: str = ".") -> float:
    """
    Return size of files in directory, excluding symbolic links.

    References:

    *   Adapted from https://stackoverflow.com/a/1392549

    """
    return sum(
        os.path.getsize(ifname)
        for (path, _, fnames) in os.walk(start_path)
        for fname in fnames
        if not os.path.islink(ifname := os.path.join(path, fname))
    )
