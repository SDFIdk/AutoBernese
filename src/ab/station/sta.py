"""
Create a stand-alone STA-file from a list of sitelog files

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

Assumptions:

*   STA-file version 1.03 (used as template).
*   Antenna serial number is '9' * 6 for type-specific calibrated.
*   The site for the given sitelog file is known to be either type- or
    individually-calibrated.

"""

import re
import logging
from typing import Any
import datetime as dt
from pathlib import Path
from dataclasses import (
    dataclass,
    asdict,
)

from ab import (
    pkg,
    country_code,
)
from ab.station.sitelog import Sitelog


log = logging.getLogger(__name__)


"""Transform sitelog data"""


Date = dt.datetime | dt.date


def create_receiver_and_antenna_change_records(
    receivers: list[dict[Any, Any]], antennae: list[dict[Any, Any]]
) -> list[dict[Any, Any]]:
    """
    Build timeline of changes in either receiver or antenna.

    """
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

        next_receiver_installed: Date = next_receiver.get("date_installed")
        next_antenna_installed: Date = next_antenna.get("date_installed")

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

    # Neither receiver nor antenna changes left
    if ix_r == ix_r_max and ix_a == ix_a_max:
        return r

    # There must only be changes left for receiver or antenna (XOR)
    assert (ix_r == ix_r_max) ^ (
        ix_a == ix_a_max
    ), f"Assumption violated: Both receiver and antenna changes available."
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
    fname: Path | str,
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
        filename=Path(fname).name,
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
        # Stripping the timestamp is a historical relic.
        #
        # Note: Sitelog format does not specify seconds.
        "00 00 00"
        "  "
        "{date_removed:10s}"
        " "
        # Stripping the timestamp is a historical relic.
        #
        # Note: Sitelog format does not specify seconds.
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

    Rules for antenna serial number and antenna number:
    *   If the antenna is individually-calibrated,
        -   use the value in the record.
        -   for the short version, use only the rightmost 5 digits in the
            number.
    *   otherwise:
        -   Use the type-calibration-convention value '999999' for antenna_no.

    """

    # By convention this value is used for type-calibrated instruments.
    type_calibrated_serial = "9" * 6

    antenna_no = antenna_serial_number[-5:]
    if type_calibration:
        antenna_no = type_calibrated_serial

    if date_removed.strip() == "":
        date_removed = "2099 12 31"

    description = city_or_town
    country_abbr = country_code.get(country)
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


def STA_created_timestamp(d: dt.datetime | dt.date = None) -> str:
    if d is None:
        d = dt.datetime.now()
    return d.strftime("%d-%b-%y %H:%M").upper()


def transform_sitelog_records_to_STA_lines(
    sitelog: Sitelog, type_calibration: bool = True
) -> dict[Any, Any]:
    """
    Create lines for STA file out of given Sitelog instance.

    """
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


def create_sta_file_from_sitelogs(
    sitelogs: list[Path | str],
    individually_calibrated: list[str] | None = None,
    output_sta_file: Path | str | None = None,
) -> None:
    """
    Combine data from given sitelog files into a STA-file.

    """

    # Defaults
    if individually_calibrated is None:
        individually_calibrated = []

    if output_sta_file is None:
        output_sta_file = "sitelogs.STA"

    # Coerce
    assert None not in sitelogs
    _sitelogs: list[Path] = [Path(path) for path in sitelogs if path is not None]

    output_sta_file = Path(output_sta_file)
    output_sta_file.parent.mkdir(parents=True, exist_ok=True)

    # Output data
    type_1_rows = []
    type_2_rows = []

    # Handle each site-log file
    for fname in sorted(_sitelogs):
        # Extract sitelog data
        log.info(f"Read {fname.name} ...")
        try:
            sitelog = Sitelog(fname)
            log.debug(f"{fname.name} read ...")
        except Exception as e:
            log.warn(f"{fname.name} could not be read: {e!r} ...")
            continue

        # Transform sitelog data
        type_calibration = sitelog.station_id not in individually_calibrated
        _1, _2 = transform_sitelog_records_to_STA_lines(sitelog, type_calibration)

        # Gather with the rest of the sitelog records
        type_1_rows.extend(_1)
        type_2_rows.extend(_2)

    # Load station data
    log.info(f"Write output to {output_sta_file} ...")
    data = dict(
        created_time=STA_created_timestamp(),
        type_1_rows="\n".join(str(row) for row in type_1_rows),
        type_2_rows="\n".join(str(row) for row in type_2_rows),
        # So far we are not using these lines
        type_3_rows="",
        type_4_rows="",
        type_5_rows="",
    )
    content = pkg.template_sta_file.read_text().format(**data)
    output_sta_file.write_text(content)
