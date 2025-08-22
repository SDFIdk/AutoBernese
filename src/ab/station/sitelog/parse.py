"""
Parse a GNSS-sitelog file to extract data needed for a STA-file

Parsed:

*   Sitelog with sections 1 through 4, extract needed fields to produce station
    history in a STA-file.

"""

import re
import logging
import collections as cs
from typing import Any

from ab.station.sitelog.models import (
    SiteIdentificationOfTheGNSSMonument,
    SiteLocationInformation,
    GNSSReceiverInformation,
    GNSSAntennaInformation,
)


log = logging.getLogger(__name__)

# META
SECTION_NUMBER = re.compile(r"[0-9]+\.([1-9]+|x)?")


def is_whitespace(s: str) -> bool:
    return not bool(s.strip())


def is_section(s: str) -> bool:
    return SECTION_NUMBER.match(s) is not None


def parse_sections(sitelog: str) -> dict[str, str]:
    """
    Opinionated sitelog parser in that it taks only the so far needed sections.

    """
    # Remove (so far) unnecessary lines
    sitelog = sitelog[sitelog.find("1.   Site Identification of the GNSS Monument") :]
    sitelog = sitelog[: sitelog.find("5.   Surveyed Local Ties")]

    # Clean up
    sitelog = sitelog.strip()

    # Remove empty lines
    lines = [line.rstrip() for line in sitelog.splitlines() if not is_whitespace(line)]

    # Slice into sections and subsections
    start_indices = [
        index for (index, line) in enumerate(lines) if is_section(line.split()[0])
    ]

    # Combine the start and end indices of each (sub)section
    slices = [
        slice(beg, end) for (beg, end) in zip(start_indices[:-1], start_indices[1:])
    ]
    slices.append(slice(start_indices[-1], -1))

    # Group subsections with sections
    """
    Create the following structure:
    {
        '1': {
            content: <section_lines>,
        },
        '2': {
            content: <section_lines>,
        },
        '3': {
            content: <section_lines>,
            subsections: [
                <subsection_lines>,
                <subsection_lines>,
                ...,
            ]
        },
        '4': {
            content: <section_lines>,
            subsections: [
                <subsection_lines>,
                <subsection_lines>,
                ...,
            ]
        }
    }
    """
    sections: cs.defaultdict[list] = cs.defaultdict(lambda: cs.defaultdict(list))
    for s in slices:
        section_lines = lines[s]
        content = "\n".join(section_lines)

        # '3.1  Receiver Type'              => ['3', '1  Receiver Type']
        # '3.   GNSS Receiver Information'  => ['3', '   GNSS Receiver Information']
        section_number, post_part = section_lines[0].split(".", maxsplit=1)

        # '1  Receiver Type'                => ['1', 'Receiver', 'Type'][0]
        # '   GNSS Receiver Information'    => ['GNSS', 'Receiver', 'Information'][0]
        subsection_number = post_part.split()[0]

        if subsection_number.lower() == "x":
            continue

        if subsection_number.isdigit():
            sections[section_number]["subsections"].append(content)
            continue

        sections[section_number]["content"] = content

    return dict(sections)


"""
Extract sitelog data from each section

"""


def compile(s: str, flags: re.RegexFlag = re.M) -> re.Pattern:
    """
    Compile pattern with *default* or specified flags

    """
    return re.compile(s, flags=flags)


# Section 1
IERS_DOMES_NUMBER = compile(r"IERS DOMES Number\s*:\s*(\S*)$")
SITE_NAME = compile(r"Site Name\s*:\s+(.*)")

FOUR_CHARACTER_ID = compile(r"Four Character ID\s+:\s+([A-Z0-9]{4}?)")
"Sitelog version 1"

NINE_CHARACTER_ID = compile(r"Nine Character ID\s+:\s+([A-Z0-9]{9})?")
"Sitelog version 2"

# Section 2
CITY_OR_TOWN = compile(r"City or Town\s+:\s+(.*)")
COUNTRY = compile(r"Country\s+(?:or Region)?\s+:\s+(.*)")

# Section 3
RECEIVER_TYPE = compile(r"Receiver Type\s+:\s(.*)")
RECEIVER_SERIAL_NUMBER = compile(r"Serial Number\s+:\s(.*)")
FIRMWARE_VERSION = compile(r"Firmware Version\s+:\s(.*)")

# Section 4
ANTENNA_TYPE = compile(r"Antenna Type\s+:\s+(.*)")
ANTENNA_SERIAL_NUMBER = compile(r"Serial Number\s+:\s+(.*)\s?[\r\n]")
MARKER_UP = compile(r"Marker->ARP Up.*\s+:\s+([\.\d]*)")
MARKER_NORTH = compile(r"Marker->ARP North.*\s+:\s+(-?[\.\d]*)")
MARKER_EAST = compile(r"Marker->ARP East.*\s+:\s+(-?[\.\d]*)")

# Common for the given sections
DATE_INSTALLED = compile(r"Date Installed\s+:\s+(\d{4})-(\d{2})-(\d{2})")
DATE_REMOVED = compile(r"Date Removed\s+:\s(\d{4})-(\d{2})-(\d{2})")

# Expansion for regular-expression search results
EXPAND_DATE = r"\1 \2 \3"

# Defaults for empty regular-expression search results
DEFAULT_MARKER = "0.0000"


# Post-process functions for expanded regular-expression search results
def post_process_marker(s: str) -> str:
    try:
        return f"{float(s):.4f}"
    except:
        return DEFAULT_MARKER


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


def value_or_default(result: re.Match | None) -> str | None:
    if result is None:
        return None
    else:
        return result[1]


def parse_section_1(s: str) -> SiteIdentificationOfTheGNSSMonument:
    return SiteIdentificationOfTheGNSSMonument(
        SITE_NAME.search(s)[1],
        value_or_default(FOUR_CHARACTER_ID.search(s)),
        value_or_default(NINE_CHARACTER_ID.search(s)),
        IERS_DOMES_NUMBER.search(s)[1],
        search_and_expand(DATE_INSTALLED, s, EXPAND_DATE),
    )


def parse_section_2(s: str) -> SiteLocationInformation:
    return SiteLocationInformation(
        CITY_OR_TOWN.search(s)[1],
        COUNTRY.search(s)[1],
    )


def parse_subsection_3(s: str) -> GNSSReceiverInformation:
    return GNSSReceiverInformation(
        RECEIVER_TYPE.search(s)[1],
        RECEIVER_SERIAL_NUMBER.search(s)[1],
        FIRMWARE_VERSION.search(s)[1],
        search_and_expand(DATE_INSTALLED, s, EXPAND_DATE),
        search_and_expand(DATE_REMOVED, s, EXPAND_DATE),
    )


def parse_subsection_4(s: str) -> GNSSAntennaInformation:
    return GNSSAntennaInformation(
        ANTENNA_TYPE.search(s)[1],
        ANTENNA_SERIAL_NUMBER.search(s)[1],
        search_and_expand(
            MARKER_UP,
            s,
            default=DEFAULT_MARKER,
            post=post_process_marker,
        ),
        search_and_expand(MARKER_NORTH, s, post=post_process_marker),
        search_and_expand(MARKER_EAST, s, post=post_process_marker),
        search_and_expand(DATE_INSTALLED, s, EXPAND_DATE),
        search_and_expand(DATE_REMOVED, s, EXPAND_DATE),
    )
