"""
Module for creating a STA-file in various ways, including:

*   Add data from a parsed sitelog file to an existing STA-file
*   (Prune existing STA-file to only include needed stations)

# The module assumes that the default STA file to merge is located at the path
# given in the configuration file.

Given:

*   STA-file version 1.03
*   Antenna serial number is '9' * 6 for type-specific calibrated.
*   The site for the given sitelog file is known to be either type- or individually-calibrated.

Be able to produce lines for the following sections of a STA 1.03-file

```
STATION INFORMATION FILE FOR BERNESE GNSS SOFTWARE 5.4           15-MAR-23 13:50
--------------------------------------------------------------------------------

FORMAT VERSION: 1.03
TECHNIQUE:      GNSS

TYPE 001: RENAMING OF STATIONS
------------------------------

STATION NAME          FLG          FROM                   TO         OLD STATION NAME      REMARK
****************      ***  YYYY MM DD HH MM SS  YYYY MM DD HH MM SS  ********************  ************************
ACOR 13434M001        001  1998 12 06 00 00 00                       ACOR*                 acor00esp_20221124.log
...

TYPE 002: STATION INFORMATION
-----------------------------

STATION NAME          FLG          FROM                   TO         RECEIVER TYPE         RECEIVER SERIAL NBR   REC #   ANTENNA TYPE          ANTENNA SERIAL NBR    ANT #    NORTH      EAST      UP     AZIMUTH  LONG NAME  DESCRIPTION             REMARK
****************      ***  YYYY MM DD HH MM SS  YYYY MM DD HH MM SS  ********************  ********************  ******  ********************  ********************  ******  ***.****  ***.****  ***.****  ****.*  *********  **********************  ************************
ACOR 13434M001        001  1998 12 06 10 10 00  2001 12 19 00 00 00  ASHTECH UZ-12                        00224     224  ASH700936D_M    SNOW                999999  999999    0.0000    0.0000    3.0420     0.0             A Coruna, ESP           UE00-0A12
ACOR 13434M001        001  2001 12 19 00 00 00  2004 04 15 00 00 00  ASHTECH UZ-12                        12109   12109  ASH700936D_M    SNOW                999999  999999    0.0000    0.0000    3.0420     0.0             A Coruna, ESP           ZC00
ACOR 13434M001        001  2004 04 15 00 00 00  2007 03 17 23 59 00  ASHTECH UZ-12                        12110   12110  ASH700936D_M    SNOW                999999  999999    0.0000    0.0000    3.0420     0.0             A Coruna, ESP           ZC00
ACOR 13434M001        001  2007 03 18 00 00 00  2008 04 21 09 00 00  LEICA GRX1200PRO                    459187  459187  LEIAT504        LEIS                999999  999999    0.0000    0.0000    3.0460     0.0             A Coruna, ESP           5.00
ACOR 13434M001        001  2008 04 21 09 30 00  2008 12 05 12 30 00  LEICA GRX1200PRO                    459187  459187  LEIAT504        LEIS                999999  999999    0.0000    0.0000    3.0460     0.0             A Coruna, ESP           5.62
ACOR 13434M001        001  2008 12 05 12 30 00  2010 02 02 09 30 00  LEICA GRX1200PRO                    459187  459187  LEIAT504        LEIS                999999  999999    0.0000    0.0000    3.0460     0.0             A Coruna, ESP           6.02
...
```

The mapping from the sitelog is such that the following sections of the sitelog should be extracted:

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
from dataclasses import dataclass
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
    return d.strftime('%d-%b-%y %H:%M').upper()


# Section 1
IERS_DOMES_NUMBER: re.Pattern = re.compile(r"IERS DOMES Number\s*:\s(.*)", flags=re.M)
SITE_NAME: re.Pattern = re.compile(r"Site Name\s*:\s+(.*)", flags=re.M)
FOUR_CHARACTER_ID: re.Pattern = re.compile(
    r"Four Character ID\s+:\s+([A-Z0-9]{4}?)", flags=re.M
)

# Section 2
CITY_OR_TOWN: re.Pattern = re.compile(r"City or Town\s+:\s+(.*)", flags=re.M)

# Section 3
RECEIVER_TYPE: re.Pattern = re.compile(r"Receiver Type\s+:\s(.*)", flags=re.M)
RECEIVER_SERIAL_NUMBER: re.Pattern = re.compile(r"Serial Number\s+:\s(.*)", flags=re.M)
FIRMWARE_VERSION: re.Pattern = re.compile(r"Firmware Version\s+:\s(.*)", flags=re.M)

# Section 4
ANTENNA_TYPE: re.Pattern = re.compile(r"Antenna Type\s+:\s+(.*)", flags=re.M)
ANTENNA_SERIAL_NUMBER: re.Pattern = re.compile(
    r"Serial Number\s+:\s+(.*)\s?[\r\n]", flags=re.M
)
MARKER_UP: re.Pattern = re.compile(r"Marker->ARP Up.*\s+:\s+(.*)", flags=re.M)
MARKER_NORTH: re.Pattern = re.compile(r"Marker->ARP North.*\s+:\s+(.*)", flags=re.M)
MARKER_EAST: re.Pattern = re.compile(r"Marker->ARP East.*\s+:\s+(.*)", flags=re.M)

# Common for the given sections
DATE_INSTALLED: re.Pattern = re.compile(
    r"Date Installed\s+:\s+(\d{4})-(\d{2})-(\d{2})", flags=re.M
)
DATE_REMOVED: re.Pattern = re.compile(
    r"Date Removed\s+:\s(\d{4})-(\d{2})-(\d{2})", flags=re.M
)

# Expansion for regular-expression search results
EXPAND_FORMAT_DATE = r"\1\2\3"

# Defaults for empty regular-expression search results
MARKER_DEFAULT = "0.0000"


# Post-process functions for expanded regular-expression search results
def post_process_marker(s: str) -> str:
    try:
        return f"{float(s):.4f}"
    except:
        return MARKER_DEFAULT


class NameSpace:
    """
    A simple container for adding various instance members for different
    purposes.

    """

    _name = "NameSpace"

    def __init__(self, name: str = None) -> None:
        if not name is None:
            self._name = name

    def __repr__(self):
        members = [m for m in dir(self) if not m.startswith("_")]
        key_value_pairs = ", ".join(
            [f'{key}="{getattr(self, key)}"' for key in members]
        )
        return f"{self._name}({key_value_pairs})"


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

    print("Post processing")
    return post(expanded)


def parse_section_1(s: str) -> Any:
    ns = NameSpace("Section1")
    ns.name = SITE_NAME.search(s)[1]
    ns.domes = IERS_DOMES_NUMBER.search(s)[1]
    return ns


def parse_section_2(s: str) -> Any:
    ns = NameSpace("Section2")
    ns.city_or_town = CITY_OR_TOWN.search(s)[1]
    return ns


def parse_subsection_3(s: str) -> Any:
    ns = NameSpace("Section3")
    ns.receiver_type = RECEIVER_TYPE.search(s)[1]
    ns.serial_number = RECEIVER_SERIAL_NUMBER.search(s)[1]
    ns.firmware = FIRMWARE_VERSION.search(s)[1]
    ns.date_installed = search_and_expand(DATE_INSTALLED, s, EXPAND_FORMAT_DATE)
    ns.date_removed = search_and_expand(DATE_REMOVED, s, EXPAND_FORMAT_DATE)
    return ns


def parse_subsection_4(s: str) -> Any:
    ns = NameSpace("Section4")
    ns.antenna_type = ANTENNA_TYPE.search(s)[1]
    ns.antenna_serial_number = ANTENNA_SERIAL_NUMBER.search(s)[1]
    ns.marker_up = search_and_expand(
        MARKER_UP, s, default=MARKER_DEFAULT, post=post_process_marker
    )
    ns.marker_north = search_and_expand(MARKER_NORTH, s, post=post_process_marker)
    ns.marker_east = search_and_expand(MARKER_EAST, s, post=post_process_marker)
    ns.date_installed = search_and_expand(DATE_INSTALLED, s, EXPAND_FORMAT_DATE)
    ns.date_removed = search_and_expand(DATE_REMOVED, s, EXPAND_FORMAT_DATE)
    return ns


"""
TO DO:

1)
Given the download module is implemented
And the single-program-execution-module is implemented and can run the STA2STA program
And the EUREF52.STA file is downloaded
And the EUREF52.STA is converted

When the EUREF54.STA file is loaded and its content is provided
And the sitelog is loaded and its content is provided
And a list of individually-calibrated sites are provided
And a list of the needed sites (no pruning if None provided)

Then create a STA-file content from the above
And send it back to the user.


"""

# @dataclass
# class Type001:
#     STATION NAME: str = '' # TODO: This is a mix of four-character ID and DOMES Number
#     FLG: str = ''
#     FROM: str = ''
#     TO: str = ''
#     RECEIVER TYPE: str = ''
#     RECEIVER SERIAL NBR: str = ''
#     REC #: str = '999999'
#     ANTENNA TYPE: str = ''
#     ANTENNA SERIAL NBR: str = ''
#     ANT #: str = ''
#     NORTH: str = ''
#     EAST: str = ''
#     UP: str = ''
#     AZIMUTH: str = ''
#     LONG NAME: str = ''
#     DESCRIPTION: str = ''
#     REMARK: str = ''

# @dataclass
# class Type002:
#     STATION NAME: str = ''
#     FLG: str = ''
#     FROM: str = ''
#     TO: str = ''
#     RECEIVER TYPE: str = ''
#     RECEIVER SERIAL NBR: str = ''
#     REC #: str = '999999'
#     ANTENNA TYPE: str = ''
#     ANTENNA SERIAL NBR: str = ''
#     ANT #: str = ''
#     NORTH: str = ''
#     EAST: str = ''
#     UP: str = ''
#     AZIMUTH: str = ''
#     LONG NAME: str = ''
#     DESCRIPTION: str = ''
#     REMARK: str = ''

    # TYPE 001: RENAMING OF STATIONS
    # ------------------------------

    # STATION NAME
    # Format: f'{site_name} {four_character_id}'
    # (SITE_NAME, '',),
    # (FOUR_CHARACTER_ID, '',),

    #
    # (DATE_INSTALLED, '',),

    # FLG=(re.compile=(r''), '',),
    # FROM=(re.compile=(r''), '',),
    # TO=(re.compile=(r''), '',),
    # RECEIVER TYPE=(re.compile=(r''), '',),
    # RECEIVER SERIAL NBR=(re.compile=(r''), '',),
    # REC_NUMBER=(re.compile(r''), '999999',),
    # ANTENNA_TYPE=(re.compile=(r''), '',),
    # ANTENNA_SERIAL_NBR=(re.compile=(r''), '',),
    # ANT_NUMBER=(re.compile=(r''), '',),
    # NORTH=(re.compile=(r''), '',),
    # EAST=(re.compile=(r''), '',),
    # UP=(re.compile=(r''), '',),
    # AZIMUTH=(re.compile=(r''), '',),
    # LONG NAME=(re.compile=(r''), '',),
    # DESCRIPTION=(re.compile=(r''), '',),
    # REMARK=(re.compile=(r''), '',),


# ---

def create_stafile_from_sitelog() -> str:
    """
    Create a working version-1.03 STA file from provided sitelogs.

    *   Read sitelog for each site.
    *   Generate lines for each STA section Type 001 and Type 002 (the others are not needed so far.)
    *

    """
    rows = dict(
        created_time=STA_created_timestamp(),
        type_1_rows = '',
        type_2_rows = '',
        type_3_rows = '',
        type_4_rows = '',
        type_5_rows = '',
    )
    sta_content = pkg.sta_template.read_text().format(**rows)
    with open('campaign.STA', 'w+') as f:
        f.write(sta_content)


def main():
    # from rich import print

    # from ab import pkg

    # sections = sitelog.parse(pkg.demo_sitelog.read_text())

    # print(parse_section_1(sections["1"]["content"]))
    # print(parse_section_2(sections["2"]["content"]))

    # for subsection in sections["3"]["subsections"]:
    #     print(parse_subsection_3(subsection))

    # for subsection in sections["4"]["subsections"]:
    #     print(parse_subsection_4(subsection))

    # for section in sections:
    #     print(sections[section]['content'])

    create_stafile_from_sitelog()


if __name__ == "__main__":
    main()
