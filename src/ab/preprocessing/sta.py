"""
Module for creating a stand-alone STA-file from a parsed sitelog.

Given:

*   STA-file version 1.03 (used as template).
*   Antenna serial number is '9' * 6 for type-specific calibrated.
*   The site for the given sitelog file is known to be either type- or
    individually-calibrated.

The mapping from the sitelog is such that the following sections of the sitelog
should be extracted:

|  Section  |     Field key     | Value format |     Used for    | STA Section |
|-----------|-------------------|--------------|-----------------|-------------|
| Section 1 |                   |              |                 |             |
|           | Four Character ID | AS-IS        | STATION NAME    |         001 |
|           | IERS DOMES Number | AS-IS        | STATION NAME    |             |
|           | Date Installed    | %y%m%d       |                 |             |
| Section 2 |                   |              |                 |             |
|           | City or Town      | AS-IS        | DESCRIPTION     |             |
| Section 3 |                   |              |                 |             |
|           | Receiver Type     | AS-IS        |                 |             |
|           | Serial Number     | AS-IS        |                 |             |
|           | Firmware Version  | AS-IS        |                 |             |
|           | Date Installed    | %y%m%d       |                 |             |
|           | Date Removed      | %y%m%d       |                 |             |
| Section 4 |                   |              |                 |             |
|           | Antenna Type      |              |                 |         002 |
|           |                   | 0.0000       | NORTH, EAST, UP |             |
|           | Serial Number     | AS-IS        |                 |             |
|           | Date Installed    | %y%m%d       |                 |             |
|           | Marker->ARP Up    | %.4f         |                 |             |
|           | Marker->ARP North | %.4f         |                 |             |
|           | Marker->ARP East  | %.4f         |                 |             |

"""
import re
import logging
from typing import Any
from dataclasses import (
    dataclass,
    asdict,
)
import datetime as dt

from ab import (
    configuration,
    pkg,
)
from ab.preprocessing import sitelog


log = logging.getLogger(__name__)


def STA_created_timestamp(d: dt.datetime | dt.date = None) -> str:
    if d is None:
        d = dt.datetime.now()
    return d.strftime("%d-%b-%y %H:%M").upper()


def compile(s: str, flags=re.M) -> re.Pattern:
    return re.compile(s, flags=flags)


# Section 1
IERS_DOMES_NUMBER = compile(r"IERS DOMES Number\s*:\s(.*)")
SITE_NAME = compile(r"Site Name\s*:\s+(.*)")
FOUR_CHARACTER_ID = compile(r"Four Character ID\s+:\s+([A-Z0-9]{4}?)")

# Section 2
CITY_OR_TOWN = compile(r"City or Town\s+:\s+(.*)")

# Section 3
RECEIVER_TYPE = compile(r"Receiver Type\s+:\s(.*)")
RECEIVER_SERIAL_NUMBER = compile(r"Serial Number\s+:\s(.*)")
FIRMWARE_VERSION = compile(r"Firmware Version\s+:\s(.*)")

# Section 4
ANTENNA_TYPE = compile(r"Antenna Type\s+:\s+(.*)")
ANTENNA_SERIAL_NUMBER = compile(r"Serial Number\s+:\s+(.*)\s?[\r\n]")
MARKER_UP = compile(r"Marker->ARP Up.*\s+:\s+(.*)")
MARKER_NORTH = compile(r"Marker->ARP North.*\s+:\s+(.*)")
MARKER_EAST = compile(r"Marker->ARP East.*\s+:\s+(.*)")

# Common for the given sections
DATE_INSTALLED = compile(r"Date Installed\s+:\s+(\d{4})-(\d{2})-(\d{2})")
DATE_REMOVED = compile(r"Date Removed\s+:\s(\d{4})-(\d{2})-(\d{2})")

# Expansion for regular-expression search results
EXPAND_DATE_SPACE = r"\1 \2 \3"
EXPAND_DATE = r"\1\2\3"

# Defaults for empty regular-expression search results
MARKER_DEFAULT = "0.0000"


# Post-process functions for expanded regular-expression search results
def post_process_marker(s: str) -> str:
    try:
        return f"{float(s):.4f}"
    except:
        return MARKER_DEFAULT


# class NameSpace:
#     """
#     A simple container for adding various instance members for different
#     purposes.

#     """

#     _name = "NameSpace"

#     def __init__(self, name: str = None) -> None:
#         if not name is None:
#             self._name = name

#     def __repr__(self):
#         members = [m for m in dir(self) if not m.startswith("_")]
#         key_value_pairs = ", ".join(
#             [f'{key}="{getattr(self, key)}"' for key in members]
#         )
#         return f"{self._name}({key_value_pairs})"


def search_and_expand(
    p: re.Pattern,
    s: str,
    /,
    r: str = r"\1",
    *,
    default: Any = "",
    post: callable = None,
) -> Any:
    """
    Search string with regular-expression pattern object and return result in
    desired format. If no result, return the default value.

    """
    if (match := p.search(s)) is None:
        return default

    expanded = match.expand(r)

    if post is None:
        return expanded

    return post(expanded)


def parse_section_1(s: str) -> dict[str, str]:
    return dict(
        site_name=SITE_NAME.search(s)[1],
        four_character_id=FOUR_CHARACTER_ID.search(s)[1],
        domes=IERS_DOMES_NUMBER.search(s)[1],
        date_installed=search_and_expand(DATE_INSTALLED, s, EXPAND_DATE_SPACE),
    )


def parse_section_2(s: str) -> dict[str, str]:
    return dict(
        city_or_town=CITY_OR_TOWN.search(s)[1],
    )


def parse_subsection_3(s: str) -> dict[str, str]:
    return dict(
        receiver_type=RECEIVER_TYPE.search(s)[1],
        serial_number=RECEIVER_SERIAL_NUMBER.search(s)[1],
        firmware=FIRMWARE_VERSION.search(s)[1],
        date_installed=search_and_expand(DATE_INSTALLED, s, EXPAND_DATE),
        date_removed=search_and_expand(DATE_REMOVED, s, EXPAND_DATE),
    )


def parse_subsection_4(s: str) -> dict[str, str]:
    return dict(
        antenna_type=ANTENNA_TYPE.search(s)[1],
        antenna_serial_number=ANTENNA_SERIAL_NUMBER.search(s)[1],
        marker_up=search_and_expand(
            MARKER_UP,
            s,
            default=MARKER_DEFAULT,
            post=post_process_marker,
        ),
        marker_north=search_and_expand(MARKER_NORTH, s, post=post_process_marker),
        marker_east=search_and_expand(MARKER_EAST, s, post=post_process_marker),
        date_installed=search_and_expand(DATE_INSTALLED, s, EXPAND_DATE),
        date_removed=search_and_expand(DATE_REMOVED, s, EXPAND_DATE),
    )


def sitelog_data(sitelog: str) -> None:
    ...


def create_stafile_from_sitelog() -> str:
    """
    Create a working version-1.03 STA file from provided sitelogs.

    *   Read sitelog for each site.
    *   Generate lines for each STA section Type 001 and Type 002 (the others are not needed so far.)
    *

    """

    rows = dict(
        created_time=STA_created_timestamp(),
        type_1_rows="",
        type_2_rows="",
        type_3_rows="",
        type_4_rows="",
        type_5_rows="",
    )
    sta_content = pkg.sta_template.read_text().format(**rows)
    with open("campaign.STA", "w+") as f:
        f.write(sta_content)


def main():
    from rich import print

    # create_stafile_from_sitelog()

    config = configuration.load()
    campaign = config.get("campaign_types").get("default")
    sitelogs2sta = campaign.get("sitelogs2sta")
    fname = sitelogs2sta.get("sitelogs")[0]
    individually_calibrated = sitelogs2sta.get("individually_calibrated")
    print(individually_calibrated)

    log.info(f"Extract data hierarchy from {fname.name}")
    sections = sitelog.parse(fname.read_text())

    log.info("Get content")
    section_1 = parse_section_1(sections["1"]["content"])
    section_2 = parse_section_2(sections["2"]["content"])
    section_3_sections = [
        parse_subsection_3(subsection) for subsection in sections["3"]["subsections"]
    ]
    section_4_sections = [
        parse_subsection_4(subsection) for subsection in sections["4"]["subsections"]
    ]

    log.info("Prepare section content: Type 001")
    # TYPE 001: RENAMING OF STATIONS
    type_1_data = dict(
        station_name="{four_character_id:4s} {domes:s}".format(**section_1),
        date_installed=section_1.get("date_installed"),
        name_old="",
        fname=fname.name,
    )

    log.info("Prepare section content: Type 002")
    # TYPE 002: STATION INFORMATION

    antenna_type = f"{...}"

    """
    Problem ascertainment:

    *

    Needed information:

    *   [x] A list of four-letter ids for individually-calibrated station

    """

    combined_sections = [
        {**subsection3, **subsection4}
        for (subsection3, subsection4) in zip(section_3_sections, section_4_sections)
    ]
    print(combined_sections[0])

    type_2_data = dict(description=section_1.get("name"))

    type_2_data_sets = (type_2_data,)

    log.info("Build .STA-lines")

    type_1_row = Type001Row(**type_1_data)
    print(type_1_row)
    raise SystemExit

    type_2_lines = [Type002Row(**type_2_data) for type_2_data in type_2_data_sets]
    print("\n".join(str(line) for line in type_2_lines))


if __name__ == "__main__":
    main()


class BaseLine:
    _line_fstr = ""

    def __str__(self) -> str:
        return self._line_fstr.format(asdict(self))


@dataclass
class Type001Row:
    """
    TYPE 001: RENAMING OF STATIONS

    """

    _line_fstr = (
        "{station_name: <16s}"
        "      001  "
        # "{yyyy: >4d} {mm:0>2d} {dd:0>2d} 00 00 00"
        "{date_installed:10s} 00 00 00"
        "                       "
        "{name_old: <20s}"
        "  "
        "{fname: <24s}"
    )
    station_name: str
    date_installed: str
    name_old: str = ""
    fname: str = ""


@dataclass
class Type002Row(BaseLine):
    """
    TYPE 002: STATION INFORMATION

    """

    type_2_line_fstr = (
        "{station_name: <16s}"
        "      001  "
        "{date_beg:19s}"
        "  "
        "{date_end:19s}"
        "  "
        "{receiver_type: <20s}"
        "  "
        "{receiver_serial: >20s}"
        "  "
        "{receiver_no: >6s}"
        "  "
        "{antenna_type: <20s}"
        "  "
        "{antenna_serial: >20s}"
        "  "
        "{antenna_no: >6s}"
        "  "
        "{north: >8.4f}"
        "  "
        "{east: >8.4f}"
        "  "
        "{up: >8.4f}"
        "  "
        "{azimuth: >6.1f}"
        "  "
        "{long_name: <9s}"  # Not used in EUREF52.STA
        "  "
        "{description: <22s}"
        "  "
        "{remark: <22s}"
    )
    station_name: str = ""

    date_beg: str = ""
    date_end: str = ""

    receiver_type: str = ""
    receiver_serial: str = ""
    receiver_no: str = "9" * 6

    antenna_type: str = ""
    antenna_serial: str = ""
    antenna_no: str = ""

    north: float = 0.0
    east: float = 0.0
    up: float = 0.0
    azimuth: float = 0.0

    long_name: str = ""
    description: str = ""
    remark: str = ""
