"""
Module for creating a stand-alone STA-file from a parsed sitelog.

Concept: Implement one sitelog translated to STA-file.

Problem ascertainment:

*   Changes occur in parallel in sections 3 (receivers) and 4 (antennae).
*   A section always has an installation date.
*   All but the last section (the current/active one) have date of removal.
*   A line in the STA file section 002 is any change in either antenna or
    receiver or both (if the install date is the exact same for both).
*   As antenna and receiver information changes are grouped toghether in this
    one line, and the change in either equipment must be accounted for, the
    timeline must be created with the different windows in which either receiver
    and antenna were active.

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
import datetime as dt
import pathlib
from dataclasses import (
    dataclass,
    asdict,
)
import functools

import yaml

from ab import (
    configuration,
    pkg,
)
from ab.sitelog import Sitelog


log = logging.getLogger(__name__)


"""Transform sitelog data"""

_COUNTRY_CODES: dict[str, str] = None


@functools.cache
def country_code(country_name: str) -> str:
    """
    Get three-letter country code for given country name if it exists in the
    package-version of the ISO 3166 standard.

    References:
    -----------
    *   [ISO 3166 Country Codes](https://www.iso.org/iso-3166-country-codes.html)

    """
    global _COUNTRY_CODES
    if _COUNTRY_CODES is None:
        _COUNTRY_CODES = yaml.safe_load(pkg.country_codes.read_text())
    return _COUNTRY_CODES.get(country_name.strip())


def create_receiver_and_antenna_change_records(
    receivers: list[dict[Any, Any]], antennae: list[dict[Any, Any]]
) -> list[dict[Any, Any]]:
    """
    Build timeline of changes in either receiver or antenna.

    """
    # TODO: Git-comit msg: Re-implement logic from perl program to refactor later
    assert (
        receivers and antennae
    ), f"Assumption violated: There must always be one receiver and antenna"

    # Note: date_installed and date_removed in the antenna section
    # overrides key-value pairs in the receiver section.
    r = [{**receivers[0], **antennae[0]}]

    # Create the timeline, looking at the installation dates for each instrument
    # (receiver or antenna)

    # Begin at the first sub section of each instrument section
    ix_r, ix_a = 0, 0

    ix_r_max = len(receivers) - 1
    ix_a_max = len(antennae) - 1

    while True:
        there_is_a_next_receiver = ix_r < ix_r_max
        there_is_a_next_antenna = ix_a < ix_a_max

        # Can we continue?
        if not there_is_a_next_receiver or not there_is_a_next_antenna:
            break

        # Current antenna and receiver
        current_receiver = receivers[ix_r]
        current_antenna = antennae[ix_a]

        # Next receiver and antenna
        next_receiver = receivers[ix_r + 1]
        next_antenna = antennae[ix_a + 1]

        next_receiver_installed = next_receiver.get("date_installed")
        next_antenna_installed = next_antenna.get("date_installed")

        # Case: next receiver installed before next antenna
        if next_receiver_installed < next_antenna_installed:
            # Use the installation data for the next receiver:
            date = next_receiver_installed

            # Set receiver and antenna record to use
            receiver = next_receiver
            antenna = current_antenna

            # Set index for current receiver in the next round of the loop
            ix_r += 1

        # Case: next antenna installed before next receiver
        elif next_receiver_installed > next_antenna_installed:
            # Use the installation data for the next antenna:
            date = next_antenna_installed

            # Set receiver and antenna record to use
            receiver = current_receiver
            antenna = next_antenna

            # Set index for current antenna in the next round of the loop
            ix_a += 1

        # Case: Antenna and receiver installed on the same date
        else:
            # Pick any of the dates, since they are the same.
            # Lets take the receiver's installation date:
            date = next_receiver_installed

            # Set receiver and antenna record to use
            receiver = next_receiver
            antenna = next_antenna

            # Set indices for current receiver and antenna in the next round of
            # the loop
            ix_r += 1
            ix_a += 1

        # Add a change record with the next change in either receiver, antenna or both
        r.append({**receiver, **antenna, **dict(date_installed=date)})

        # Set end date on previous change record
        r[-2]["date_removed"] = date

    # At this point, either there are no more sub sections with receiver changes or antenna changes

    # Could both be the case?
    assert (ix_r == ix_r_max) ^ (
        ix_a == ix_a_max
    ), f"Assumption violated: Both receivers and antennae changes available."
    # No: either one instrument has more changes or none.
    # If no changes are left for either, the following while loops will not run.

    # Take receiver changes first
    while ix_r < ix_r_max:
        ix_r += 1
        receiver = receivers[ix_r]
        antenna = antennae[ix_a]
        r.append({**antenna, **receiver})
        # Set date removed on previous change to that of current change
        r[-2]["date_removed"] = r[-1]["date_installed"]

    while ix_a < len(antennae) - 1:
        ix_a += 1
        receiver = receivers[ix_r]
        antenna = antennae[ix_a]
        # Note that the order is different here, since the change is in the
        # antenna, and data from this change must update the dict last.
        r.append({**receiver, **antenna})
        # Set date removed on previous change to that of current change
        r[-2]["date_removed"] = r[-1]["date_installed"]

    return r


def __repr__(self) -> str:
    """
    Common __repr__ for dataclasses created for each STA Type 00X row.

    Note: Can not figure out, why inheritance from a base class does not work.
    Repeating myself for now.

    """
    return self._fstr.format(**asdict(self)).strip()


@dataclass
class Type001Row:
    """
    Data for a single line in section `TYPE 001: RENAMING OF STATIONS` of a STA
    file.

    When `print()`'ed or otherwise formatted as a string, the instance yields a
    line with the data formatted according to STA-file format version 1.03.

    """

    station_name: str
    date_installed: str
    name_old: str
    filename: str

    _fstr = (
        "{station_name: <16s}"
        "      001  "
        # "{yyyy: >4d} {mm:0>2d} {dd:0>2d} 00 00 00"
        "{date_installed:10s} 00 00 00"
        "                       "
        "{name_old: <20s}"
        "  "
        "{filename: <24s}"
    )

    __repr__ = __repr__


def station_name(four_character_id: str, domes: str) -> str:
    return f"{four_character_id:4s} {domes:s}"


def map_to_type_1_row(
    four_character_id: str,
    domes: str,
    date_installed: str,
    fname: pathlib.Path | str,
    **_,
) -> dict[str, str]:
    """
    Build a record for section Type 001 in a STA file.

    Map sitelog section-1 data to key-value pairs needed for a row in the
    STA-file section `TYPE 001: RENAMING OF STATIONS`

    """
    return dict(
        station_name=station_name(four_character_id, domes),
        date_installed=date_installed,
        name_old=f"{four_character_id}*",
        filename=pathlib.Path(fname).name,
    )


@dataclass
class Type002Row:
    """
    Data for a single line in section `TYPE 002: STATION INFORMATION` of a STA
    file.

    When `print()`'ed or otherwise formatted as a string, the instance yields a
    line with the data formatted according to STA-file format version 1.03.

    """

    station_name: str = ""

    date_installed: str = ""
    date_removed: str = "2099 12 31"

    receiver_type: str = ""
    receiver_serial_number: str = ""
    # By convention this value is used for type-calibrated instruments.
    receiver_no: str = "9" * 6

    antenna_type: str = ""
    antenna_serial_number: str = ""
    antenna_no: str = ""

    marker_north: float = 0.0
    marker_east: float = 0.0
    marker_up: float = 0.0
    azimuth: float = 0.0

    long_name: str = ""
    description: str = ""
    remark: str = ""

    _fstr = (
        "{station_name: <16s}"
        "      001  "
        "{date_installed:10s}"
        " "
        # This is bad, but a historical relic. TODO: Change this to include %H
        # and %M. Sitelog format does not specify seconds.
        "00 00 00"
        "  "
        "{date_removed:10s}"
        " "
        # This is bad, but a historical relic. TODO: Change this to include %H
        # and %M. Sitelog format does not specify seconds.
        "00 00 00"
        "  "
        "{receiver_type: <20s}"
        "  "
        "{receiver_serial_number: >20s}"
        "  "
        "{receiver_no: >6s}"
        "  "
        "{antenna_type: <20s}"
        "  "
        "{antenna_serial_number: >20s}"
        "  "
        "{antenna_no: >6s}"
        "  "
        "{marker_north: >8.4f}"
        "  "
        "{marker_east: >8.4f}"
        "  "
        "{marker_up: >8.4f}"
        "  "
        "{azimuth: >6.1f}"
        "  "
        "{long_name: <9s}"  # Not used in EUREF52.STA
        "  "
        "{description: <22s}"
        "  "
        "{remark: <22s}"
    )

    __repr__ = __repr__


NON_DIGITS = re.compile(r"\D*", flags=re.M | re.S)


def build_receiver_no(receiver_serial_number: str) -> str:
    """

    Build a short number for the `Rec #` column in the Type002-section of the
    STA file.

    From visual inspection, it is clear that the build rule is like this:

    *   Remove letters (and probably everything besides arabic numerals) from the serial number.
    *   Take only the rightmost six numbers.
    *   Remove leading zeros, keep the rest.

    References:
    -----------

    *   EUREF52.STA (fetched Winter 2023)

    """
    replaced = NON_DIGITS.sub("", receiver_serial_number)
    if replaced == "":
        return replaced
    return f"{int(replaced[-6:])}"


def map_to_type_2_row(
    # Section 1
    four_character_id: str,
    domes: str,
    # Section 2
    city_or_town: str,
    country: str,
    # Campaign configuration
    type_calibration: bool,
    # Receiver/antenna change record
    receiver_type: str,
    receiver_serial_number: str,
    firmware: str,
    date_installed: str,
    date_removed: str,
    antenna_type: str,
    antenna_serial_number: str,
    marker_up: str,
    marker_north: str,
    marker_east: str,
    **_,
) -> dict[str, str]:
    """
    Build a record for section Type 002 in a STA file.

    Map sitelog section-2 data to key-value pairs needed for a row in
    the STA-file section `TYPE 002: STATION INFORMATION`

    """
    # Rules for antenna serial number and antenna number:
    # *   If the antenna is individually-calibrated,
    #     -   use the value in the record.
    #     -   for the short version, use only the rightmost 5 digits in the
    #         number.
    # *   otherwise:
    #     -   Use the type-calibration-convention value '999999' for both values.

    # By convention this value is used for type-calibrated instruments.
    type_calibrated_serial = "9" * 6

    antenna_no = antenna_serial_number[-5:]
    if type_calibration:
        # antenna_serial_number = type_calibrated_serial
        antenna_no = type_calibrated_serial

    if date_removed.strip() == "":
        date_removed = "2099 12 31"

    description = city_or_town
    country_abbr = country_code(country)
    if country_abbr is not None:
        description = f"{description}, {country_abbr}"

    return dict(
        station_name=station_name(four_character_id, domes),
        date_installed=date_installed,
        date_removed=date_removed,
        receiver_type=receiver_type,
        receiver_serial_number=receiver_serial_number,
        receiver_no=build_receiver_no(receiver_serial_number),
        antenna_type=antenna_type,
        antenna_serial_number=antenna_serial_number,
        antenna_no=antenna_no,
        marker_north=float(marker_north),
        marker_east=float(marker_east),
        marker_up=float(marker_up),
        azimuth=0.0,
        long_name="",
        description=description,
        remark=firmware,
    )


# Load
# ----


def STA_created_timestamp(d: dt.datetime | dt.date = None) -> str:
    if d is None:
        d = dt.datetime.now()
    return d.strftime("%d-%b-%y %H:%M").upper()


# Main
# ----


def transform_sitelog_records_to_STA_lines(
    sitelog: Sitelog, type_calibration: bool = True
) -> dict[Any, Any]:
    log.info(f"Build Type-001 line for {sitelog.filename.name}")
    prepared = {**sitelog.section_1, **dict(fname=sitelog.filename)}
    type_1_lines = [Type001Row(**map_to_type_1_row(**prepared))]

    log.info(f"Build Type-002 lines for {sitelog.filename.name}")
    type_2_data = create_receiver_and_antenna_change_records(
        sitelog.receivers, sitelog.antennae
    )

    calibration = dict(type_calibration=type_calibration)
    constants = {**sitelog.section_1, **sitelog.section_2, **calibration}
    type_2_rows = [
        map_to_type_2_row(**{**constants, **change_record})
        for change_record in type_2_data
    ]
    type_2_lines = [Type002Row(**parameters) for parameters in type_2_rows]

    return type_1_lines, type_2_lines


def main():
    # General configuration
    config = configuration.load()
    station_meta = config.get("station_meta")
    individually_calibrated = station_meta.get("individually_calibrated")
    sitelog_filenames = station_meta.get("sitelogs")

    # Campaign configuration
    # TODO: Have a campaign configuration file, and if none given, use the
    # default campaign configuration.
    campaign = config.get("campaign_types").get("default")

    # Combine several sitelogs converted to STa-data for a single STA-file.
    type_1_rows = []
    type_2_rows = []

    # TODO: Remove rich import
    from rich import print

    for fname in sorted(sitelog_filenames):
        # Extract sitelog data
        print(f'Read {fname.name} ...', end='')
        try:
            sitelog = Sitelog(fname)
            print('[green][ OK ][/green]')
        except:
            print('[red][ BAD ][/red]')
            continue

        # Transform sitelog data
        type_calibration = sitelog.station_id not in individually_calibrated
        _1, _2 = transform_sitelog_records_to_STA_lines(sitelog, type_calibration)

        # Gather with the rest of the sitelog records
        type_1_rows.extend(_1)
        type_2_rows.extend(_2)

    log.info("Build .STA-file")

    # Load station data
    data = dict(
        created_time=STA_created_timestamp(),
        type_1_rows="\n".join(str(row) for row in type_1_rows),
        type_2_rows="\n".join(str(row) for row in type_2_rows),
        # So far we are not using these lines
        type_3_rows="",
        type_4_rows="",
        type_5_rows="",
    )
    sta_content = pkg.sta_template.read_text().format(**data)

    # Save the data
    # TODO: Store it in the campaign directory
    ofname = pathlib.Path(".") / "campaign.STA"
    ofname.write_text(sta_content)
