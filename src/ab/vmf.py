"""
Module for building .GRD-files for each day.

"""
from typing import (
    Any,
    Final,
)
import datetime as dt
from pathlib import Path
from dataclasses import dataclass
import logging

from ab.dates import (
    date_range,
    GPSDate,
)
from ab.parameters import (
    resolved,
)


log = logging.getLogger(__name__)

# _EARLIEST: Final[dt.date] = dt.date(2008, 1, 1)  # First date with data on the source server.
_EARLIEST: Final[dt.date] = dt.date(2023, 1, 1)

_FSTR_IFNAME: Final[str] = "VMF3_{date.year}{date.month:02d}{date.day:02d}.H{hour}"
_FSTR_IFNAME_YEAR_SUBDIR: Final[
    str
] = "{date.year}/VMF3_{date.year}{date.month:02d}{date.day:02d}.H{hour}"
_FSTR_OFNAME: Final[str] = "VMFG_{date.year}{date.doy:03d}0.GRD"

_HOURS: Final[list[str]] = ["00", "06", "12", "18"]


def status(ipath: Path | str, opath: Path | str, /) -> list[dt.date]:
    """
    Return status for each date for which there should be data available.

    """
    yesterday = dt.date.today() - dt.timedelta(days=1)
    data_days = date_range(_EARLIEST, yesterday, transformer=GPSDate)
    # return len(data_days)

    vmf_files = [VMF3DayFile(date, ipath, opath) for date in data_days]
    return [vmf_file.status() for vmf_file in vmf_files]


def build(ipath: Path | str, opath: Path | str, /) -> list[dt.date]:
    """
    Build day file for each date for which there be data available.

    """
    yesterday = dt.date.today() - dt.timedelta(days=1)
    data_days = date_range(_EARLIEST, yesterday, transformer=GPSDate)
    vmf_files = [VMF3DayFile(date, ipath, opath) for date in data_days]
    for vmf_file in vmf_files:
        vmf_file.build()


def _input_filenames(date: dt.date | dt.datetime, *, year_subdir: bool = True) -> str:
    """
    Return filenames ending with H00, H06, H12 and H18 for given date and
    filename ending with H00 for the following date

    """
    parameters = dict(date=[date], hour=_HOURS)
    combinations = resolved(parameters)
    combinations.append(dict(date=date + dt.timedelta(1), hour=_HOURS[0]))
    fstr = _FSTR_IFNAME_YEAR_SUBDIR if year_subdir else _FSTR_IFNAME
    return [fstr.format(**c) for c in combinations]


@dataclass
class VMF3DayFile:
    date: dt.date | dt.datetime
    ipath: str
    opath: Path | str

    def __post_init__(self) -> None:
        self.ipath = Path(self.ipath)
        self.opath = Path(self.opath)

    def resolve_input_files(self) -> list[str]:
        return [self.ipath / fname for fname in _input_filenames(self.date)]

    @property
    def input_available(self):
        return all(path.is_file() for path in self.resolve_input_files())

    @property
    def output_file(self) -> Path:
        return self.opath / _FSTR_OFNAME.format(date=self.date)

    @property
    def exists(self) -> bool:
        return self.output_file.is_file()

    def build(self) -> None:
        if not self.input_available:
            log.warn(f"Missing input files for {self} ...")
            return
        ifnames = self.resolve_input_files()
        fstr = "{}\n" * len(ifnames)
        contents = [ifname.read_text() for ifname in ifnames]
        self.output_file.resolve().parent.mkdir(exist_ok=True, parents=True)
        self.output_file.write_text(fstr.format(*contents))

    def status(self) -> dict[str, Any]:
        return dict(
            date=self.date.isoformat(),
            input_available=self.input_available,
            output_file_exists=self.exists,
        )
