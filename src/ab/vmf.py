"""
Work with gridded troposphere data from Technical University of Vienna presuming
specifically data from the Vienna Mapping Function 3 (VMF3).

The goal is to concatenate data files from a given day covering intervals of
that day into a single file with data for that entire day.

"""

from typing import Final
from collections.abc import Iterator
import datetime as dt
from pathlib import Path
from dataclasses import dataclass

# import linecache
from itertools import islice
import logging

from ab.dates import (
    date_range,
    dates_to_gps_date,
    GPSDate,
)
from ab.parameters import (
    permutations,
    ParametersType,
    PermutationType,
)


log = logging.getLogger(__name__)


# Filename structure

_HOURS: Final = ["00", "06", "12", "18"]
"Hours during the day at which source files are supplied."


# Quality assurrance and control

N_FILES_H: Final = 5
"Number of input hour files"

N_LINES_H: Final = 64807
"Number of lines in an hour file"

IX_LINE_MAX: Final = N_LINES_H - 1
"Line index of the last line in an hour file"

INDEX_EPOCH_LINE: Final = 3
"Index of a line that is unique to each hour file"


def _input_filepaths(
    path: Path, fname: Path | str, date: dt.date | dt.datetime
) -> list[Path]:
    """
    Return file paths ending with H00, H06, H12 and H18 for given date and
    filename ending with H00 for the following date

    """
    parameters: ParametersType = dict(date=[date], hour=_HOURS)
    extra: PermutationType = dict(date=date + dt.timedelta(1), hour=_HOURS[0])
    permutations_ = permutations(parameters) + [extra]
    fstr = str(path / fname)
    return [Path(fstr.format(**permutation)) for permutation in permutations_]


def _output_filepath(
    path: Path, fname: Path | str, date: dt.date | dt.datetime
) -> Path:
    """
    Return file path for the output file for the given date.

    """
    return Path(str(path / fname).format(date=date))


def concatenate(*parts: str) -> str:
    """
    Concatenate string content without separator

    """
    return ("{}" * len(parts)).format(*parts)


@dataclass
class VMFDataStatus:
    date: str
    input_available: bool
    output_file_exists: bool
    output_file: str


@dataclass
class DayFileBuilder:
    date: GPSDate
    ipath: Path | str
    opath: Path | str
    ifname: Path | str
    ofname: Path | str

    def __post_init__(self) -> None:
        """
        Build paths, but not checking for existence

        """
        self.ipath = Path(self.ipath)
        self.opath = Path(self.opath)
        self.hour_files = _input_filepaths(self.ipath, self.ifname, self.date)
        self.day_file = _output_filepath(self.opath, self.ofname, self.date)

    @property
    def input_available(self) -> bool:
        """
        Validate existence of necessary input files

        """
        return all(path.is_file() for path in self.hour_files)

    def build(self) -> str:
        """
        Build output path and file based on existing input files and check that
        output file contains input data.

        """
        msg = ""
        if not self.input_available:
            msg = f"Missing some or all input HOUR files ..."
            log.warn(msg)
            return msg

        # Build
        contents = [ifname.read_text() for ifname in self.hour_files]
        self.day_file.resolve().parent.mkdir(exist_ok=True, parents=True)
        self.day_file.write_text(concatenate(*contents))

        # Quality control on live Python instances: Check that the unique epoch
        # line in each hour file is included in the concatenated day file.
        epoch_lines = []
        for lines in contents:
            for ix, line in enumerate(lines):
                if ix == 3:
                    epoch_lines.append(line)
                    break

        dayfile_content = self.day_file.read_text()
        missing = []
        for epoch_line in epoch_lines:
            if not epoch_line in dayfile_content:
                missing.append(epoch_line)

        if missing:
            msg = "Missing epoch lines:" "\n".join(f'* "{line}"' for line in missing)

        return msg

        if not self.day_file.is_file():
            msg = f"Failed to create output file {self.day_file} ..."

        return msg

    def check(self) -> str:
        """
        Load input and output files and make reasonably sure that content of
        input files are correctly copied to the output file.

        """
        # Default return message
        msg = ""

        # Check that the operation can be performed
        s = self.status()

        if not s.input_available:
            msg = f"Missing input files ..."
            return msg

        elif not s.output_file_exists:
            msg = f"Missing output file ..."
            return msg

        # Set up and begin checks
        # Offsets are relative to the position of last extraction
        INDEX_OFFSETS_ITERATOR = [
            INDEX_EPOCH_LINE,
            IX_LINE_MAX,
            IX_LINE_MAX,
            IX_LINE_MAX,
            IX_LINE_MAX,
        ]

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
        # dayfile_content = self.day_file.read_text()
        # missing = []
        # for epoch_line in epoch_lines:
        #     if not epoch_line in dayfile_content:
        #         missing.append(epoch_line)

        # 2)
        extracted_lines = []
        with open(self.day_file) as fp:
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

    def status(self) -> VMFDataStatus:
        """
        Return data structure with status for input and output data.

        """
        return VMFDataStatus(
            self.date.isoformat()[:10],
            self.input_available,
            self.day_file.is_file(),
            str(self.day_file),
        )


def day_file_builders(
    ipath: Path | str,
    opath: Path | str,
    beg: dt.date,
    end: dt.date,
    ifname: Path | str,
    ofname: Path | str,
) -> Iterator[DayFileBuilder]:
    """
    Return an iterator of DayFileBuilder instances with fixed input and output
    paths and dates ranging between beginning and end date both inclusive.

    """
    return (
        DayFileBuilder(date, ipath, opath, ifname, ofname)
        for date in dates_to_gps_date(date_range(beg, end))
    )


def build(builder: DayFileBuilder) -> str:
    return builder.build()


def check(builder: DayFileBuilder) -> str:
    return builder.check()
