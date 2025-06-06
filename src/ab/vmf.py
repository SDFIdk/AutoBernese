"""
Work with gridded troposphere data from Technical University of Vienna presuming
specifically data from the Vienna Mapping Function 3 (VMF3).

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
    dates_to_gps_date,
    GPSDate,
)
from ab.parameters import (
    permutations,
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
    parameters: dict[str, Iterable[Any]] = dict(date=[date], hour=_HOURS)
    permutations_ = permutations(parameters)
    permutations_.append(dict(date=date + dt.timedelta(1), hour=_HOURS[0]))
    return [
        Path(str(path / _FSTR_IFNAME).format(**permutation))
        for permutation in permutations_
    ]


def concatenate(*parts: str) -> str:
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
            msg = f"Missing some or all input HOUR files ..."
            log.warn(msg)
            return msg

        # Build
        contents = [ifname.read_text() for ifname in self.hour_files]
        self.dayfile.resolve().parent.mkdir(exist_ok=True, parents=True)
        self.dayfile.write_text(concatenate(*contents))

        # Quality control: Check that the unique epoch line in each hour file is
        # included in the concatenated day file.
        epoch_lines = []
        for lines in contents:
            for ix, line in enumerate(lines):
                if ix == 3:
                    epoch_lines.append(line)
                    break

        dayfile_content = self.dayfile.read_text()
        missing = []
        for epoch_line in epoch_lines:
            if not epoch_line in dayfile_content:
                missing.append(epoch_line)

        if missing:
            msg = "Missing epoch lines:" "\n".join(f'* "{line}"' for line in missing)

        return msg

        if not self.dayfile.is_file():
            msg = f"Failed to create output file {self.dayfile} ..."

        return msg

    def test(self) -> str:
        import linecache
        from itertools import islice

        N_FILES_H = 5
        N_LINES_H = 64807
        IX_LINE_MAX = N_LINES_H - 1

        INDEX_EPOCH_LINE = 3

        # Offsets are relative to the position of last extraction
        INDEX_OFFSETS_ITERATOR = [
            INDEX_EPOCH_LINE,
            IX_LINE_MAX,
            IX_LINE_MAX,
            IX_LINE_MAX,
            IX_LINE_MAX,
        ]

        msg = ""
        s = self.status()

        if not s["input_available"]:
            msg = f"Missing input files ..."
            return msg

        elif not s["output_file_exists"]:
            msg = f"Missing output file ..."
            return msg

        epoch_lines = []
        for ifname in self.hour_files:
            # 1)
            # with open(ifname) as fp:
            #     for ix, line in enumerate(fp):
            #         if ix == 3:
            #             epoch_lines.append(line)
            #             break

            # 2)
            # line = linecache.getline(str(ifname), 4)
            # if line:
            #     epoch_lines.append(line)

            # 3)
            with open(ifname) as fp:
                for line in islice(fp, INDEX_EPOCH_LINE, INDEX_EPOCH_LINE + 1):
                    epoch_lines.append(line)

        if not len(epoch_lines) == N_FILES_H:
            msg = f"Missing lines with Epoch in HOUR files for {self} ..."
            return msg

        # 1)
        # dayfile_content = self.dayfile.read_text()
        # missing = []
        # for epoch_line in epoch_lines:
        #     if not epoch_line in dayfile_content:
        #         missing.append(epoch_line)

        # 2)
        extracted_lines = []
        with open(self.dayfile) as fp:
            for ix in INDEX_OFFSETS_ITERATOR:
                # fp.seek(0)
                for line in islice(fp, ix, ix + 1):
                    extracted_lines.append(line)

        # print()
        # print('\n'.join(str(ix) for ix in INDICES))
        # for (a, b) in zip(epoch_lines, extracted_lines):
        #     print(f"a: {a}b: {b}")
        # print()
        # for debug_info in DEBUG_INDICES_ACTUAL:
        #     print(debug_info)
        # raise SystemExit

        if not len(extracted_lines) == N_FILES_H:
            msg = f"Missing lines with Epoch in DAY file for {self} ..."
            return msg

        missing = []
        for epoch_line, extracted_line in zip(epoch_lines, extracted_lines):
            if epoch_line != extracted_line:
                missing.append(epoch_line)

        if missing:
            msg = "Missing epoch lines:" "\n".join(
                f'* "{line.strip()}"' for line in missing
            )

        return msg

    def status(self) -> dict[str, Any]:
        return dict(
            date=self.date.isoformat()[:10],
            input_available=self.input_available,
            output_file_exists=self.dayfile.is_file(),
            output_file=str(self.dayfile),
        )


def day_file_builders(
    ipath: Path | str, opath: Path | str, beg: dt.date, end: dt.date
) -> Iterable[DayFileBuilder]:
    return (
        DayFileBuilder(date, ipath, opath)
        for date in dates_to_gps_date(date_range(beg, end))
    )
