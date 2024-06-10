"""
Module for building .GRD-files for each day.

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
_LATEST: Final = dt.date.today() - dt.timedelta(1)

_FSTR_IFNAME: Final = (
    "{date.year}/VMF3_{date.year}{date.month:02d}{date.day:02d}.H{hour}"
)
_FSTR_OFNAME: Final = "{date.year}/VMFG_{date.year}{date.doy:03d}0.GRD"

_HOURS: Final = ["00", "06", "12", "18"]


def _input_filenames(date: dt.date | dt.datetime) -> list[str]:
    """
    Return filenames ending with H00, H06, H12 and H18 for given date and
    filename ending with H00 for the following date

    """
    parameters = dict(date=[date], hour=_HOURS)
    combinations = resolved(parameters)
    combinations.append(dict(date=date + dt.timedelta(1), hour=_HOURS[0]))
    return [_FSTR_IFNAME.format(**c) for c in combinations]


def concatenate(*parts: list[str]) -> str:
    return ("{}\n" * len(parts)).format(*parts)


@dataclass
class DayFileBuilder:
    date: GPSDate
    ipath: Path | str
    opath: Path | str

    def __post_init__(self) -> None:
        self.ipath = Path(self.ipath)
        self.opath = Path(self.opath)
        self.hour_files: list[Path] = [
            self.ipath / fname for fname in _input_filenames(self.date)
        ]
        self.dayfile: Path = self.opath / _FSTR_OFNAME.format(date=self.date)

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
            date=self.date.isoformat(),
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
