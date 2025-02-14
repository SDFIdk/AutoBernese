"""
A module for working with gridded troposphere data from Technical University of
Vienna presuming specifically data from the Vienna Mapping Function 3 (VMF3).

The goal is to concatenate data files from a given day covering intervals of
that day into a single file with data for that entire day.

"""

from typing import (
    Any,
    Final,
    Iterable,
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

# First date with data on the source server.
_EARLIEST: Final = dt.date(2008, 1, 1)
_LATEST: Final = dt.date.today() - dt.timedelta(days=1)

_FSTR_IFNAME: Final = "VMF3_{date.year}{date.month:02d}{date.day:02d}.H{hour}"
_FSTR_OFNAME: Final = "VMF3_{date.year}{date.doy:03d}0.GRD"

_HOURS: Final = ["00", "06", "12", "18"]


def _input_filepaths(path: Path, date: dt.date | dt.datetime) -> list[Path]:
    """
    Return file paths ending with H00, H06, H12 and H18 for given date and
    filename ending with H00 for the following date

    """
    parameters = dict(date=[date], hour=_HOURS)
    combinations = resolved(parameters)
    combinations.append(dict(date=date + dt.timedelta(1), hour=_HOURS[0]))
    return [Path(str(path / _FSTR_IFNAME).format(**c)) for c in combinations]


def concatenate(*parts: list[str]) -> str:
    return ("{}" * len(parts)).format(*parts)


@dataclass
class DayFileBuilder:
    date: GPSDate
    ipath: Path | str
    opath: Path | str

    def __post_init__(self) -> None:
        self.ipath = Path(self.ipath)
        self.opath = Path(self.opath)
        self.hour_files: list[Path] = _input_filepaths(self.ipath, self.date)
        self.dayfile: Path = Path(str(self.opath / _FSTR_OFNAME).format(date=self.date))

    @property
    def input_available(self):
        return all(path.is_file() for path in self.hour_files)

    def build(self) -> str:
        msg = ""
        if not self.input_available:
            msg = f"Missing input files for {self} ..."
            log.warn(msg)
            return msg

        contents = [ifname.read_text() for ifname in self.hour_files]
        self.dayfile.resolve().parent.mkdir(exist_ok=True, parents=True)
        self.dayfile.write_text(concatenate(*contents))

        if not self.dayfile.is_file():
            msg = f"Failed to create output file {self.dayfile} ..."

        return msg

    def status(self) -> dict[str, Any]:
        return dict(
            date=self.date.isoformat()[:10],
            input_available=self.input_available,
            output_file_exists=self.dayfile.is_file(),
            output_file=str(self.dayfile),
        )


def day_file_builders(
    ipath: Path | str, opath: Path | str, beg: dt.date | None, end: dt.date | None
) -> Iterable[DayFileBuilder]:
    return (
        DayFileBuilder(date, ipath, opath)
        for date in date_range(beg, end, transformer=GPSDate)
    )
