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
# _EARLIEST: Final[dt.date] = dt.date(2008, 1, 1)
_EARLIEST: Final[dt.date] = dt.date(2023, 1, 1)

_FSTR_IFNAME: Final[str] = "VMF3_{date.year}{date.month:02d}{date.day:02d}.H{hour}"
_FSTR_IFNAME_YEAR_SUBDIR: Final[
    str
] = "{date.year}/VMF3_{date.year}{date.month:02d}{date.day:02d}.H{hour}"
_FSTR_OFNAME: Final[str] = "VMFG_{date.year}{date.doy:03d}0.GRD"

_HOURS: Final[list[str]] = ["00", "06", "12", "18"]


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

    def build(self) -> str:
        msg = ""
        if not self.input_available:
            msg = f"Missing input files for {self} ..."
            log.warn(msg)
            return msg
        ifnames = self.resolve_input_files()
        fstr = "{}\n" * len(ifnames)
        contents = [ifname.read_text() for ifname in ifnames]
        self.output_file.resolve().parent.mkdir(exist_ok=True, parents=True)
        self.output_file.write_text(fstr.format(*contents))

        if not self.exists:
            msg = f"Failed to create output file {self.output_file} ..."

        return msg

    def status(self) -> dict[str, Any]:
        return dict(
            date=self.date.isoformat(),
            input_available=self.input_available,
            output_file_exists=self.exists,
            output_file=str(self.output_file),
        )


def vmf_files(
    ipath: Path | str, opath: Path | str, beg: dt.date | None, end: dt.date | None
) -> Iterable[VMF3DayFile]:
    yesterday = dt.date.today() - dt.timedelta(days=1)
    beg = beg if beg is not None or beg <= _EARLIEST else _EARLIEST
    end = end if end is not None or end <= yesterday else yesterday
    log.info(f"VMF3 file interval is set to {beg} to {end} ...")
    data_days = date_range(beg, end, transformer=GPSDate)
    return (VMF3DayFile(date, ipath, opath) for date in data_days)
