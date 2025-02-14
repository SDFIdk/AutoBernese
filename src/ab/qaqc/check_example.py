"""
The purpose of this module is to quickly verify that results in the Bernese
installation are reliable.

Overall observations, when comparing the _REF-files with the generated output:

*   The _REF-file has only the stations it needed for the calculation, whereas
    the output files from our own run produces files with many more lines,
    since, apparently, the input station data include many more files.

*   It is not clear from the documentation of the update process, what,
    specifically, to compare, and how much it may deviate from the baseline
    results.

    Quote from README_SAVEDISK.TXT:

    > You should obtain the same results (apart from effects introduced by
    > different compilers and/or operating systems which have been used).

    Quote from README_FIRST_STEPS.md:

    > We expect no (significant) differences between your solution and the
    > reference files.

Recommendations from our internal point of view:

*   Most important to compare coordinates.
*   For coordinate files, compare *.CRD -   Criteria:
    -   well under a mm; at least 1/10 mm, and probably lower.
*   Generally, compare *.PRC files (summary files): -   Compare, e.g.:
    -   Solved ambiguities
    -   Some residuals from Helmert transformations.
    -   "Coordinate repeatability".

Files of concern:

*   Final coordinates from the RINEX-to-SINEX PCF `RNX2SNX.PCF`:
    -   $S/RNX2SNX/yyyy/FIN_yyyyssss.CRD
    -   $S/RNX2SNX/yyyy/FIN_yyyyssss.CRD_REF

"""

from dataclasses import dataclass
from pathlib import Path
from typing import (
    Protocol,
    TypeVar,
)

from ab import configuration


C = TypeVar("C", bound="Comparable")


class Comparable(Protocol):
    def __sub__(self, other: C) -> C:
        ...

    __rsub__ = __sub__


@dataclass
class FilePair:
    ref: Path
    res: Path


def get_available_comparables() -> list[FilePair]:
    config = configuration.load()
    return [
        FilePair(ref, res)
        for pair in config.get("bsw_files", {}).get("check_install", [])
        if (ref := pair.get("reference")).is_file()
        and (res := pair.get("result")).is_file()
    ]


@dataclass
class LineCRD:
    station: str
    x: float
    y: float
    z: float
    flag: str

    def __sub__(self, other: "LineCRD") -> "LineCRD":
        if not self.station == other.station:
            raise RuntimeError(
                f"Must subtract from the same station. Got {self.station!r} and {other.station!r}"
            )
        return LineCRD(
            self.station,
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
            self.flag,
        )

    __rsub__ = __sub__


@dataclass
class FileCRD:
    title: str
    date: str
    coordinates: list[LineCRD]

    def __sub__(self, other: "FileCRD") -> "FileCRD":
        diffs = [
            self_line - other_line
            for (self_line, other_line) in zip(self.coordinates, other.coordinates)
        ]
        return FileCRD(self.title, self.date, diffs)

    __rsub__ = __sub__


def extract_coordinates(raw: str) -> FileCRD:
    FLAG_INDEX: int = 70

    results = []
    for index, line in enumerate(raw.splitlines()):
        if index == 0:
            # Save metadata
            title = line[:-15].strip().split(":")[0]
            date = line[-15:]
            continue
        if index < 7:
            # Not a line with coordinate results
            continue
        if not len(line) > FLAG_INDEX:
            # Not calculated
            continue
        results.append(line)

    coordinates = []  ## TODO: Make it a dict with station as key
    for line in results:
        coordinates.append(
            LineCRD(
                station=line[5:9],
                x=float(line[20:36]),
                y=float(line[37:51]),
                z=float(line[52:66]),
                flag=line[FLAG_INDEX],
            )
        )
    return FileCRD(title, date, coordinates)


def flag_if_too_high(delta: float, tolerance: float = 0.0001) -> str:
    return "!" if abs(delta) > tolerance else " "
