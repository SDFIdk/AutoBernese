"""
Check if all variables in LOADGPS.setvar script have been set

"""

from typing import Final
import os


KEYS: Final = (
    "VERSION",
    "F_VERS",
    "F_VERS_LIST",
    "C",
    "SRC",
    "LG",
    "FG",
    "XG",
    "XQ",
    "SPT",
    "BPE",
    "EXE",
    "SUP",
    "DOC",
    "HLP",
    "PAN",
    "GLOBAL",
    "MODEL",
    "CONFIG",
    "USR",
    "OPT",
    "PCF",
    "SCR",
    "BPE_SERVER_HOST",
    "U",
    "T",
    "P",
    "D",
    "S",
    "QTBERN",
    "OS",
    "OS_NAME",
    "CGROUP",
)


def sourced() -> bool:
    for key in KEYS:
        if key not in os.environ:
            return False
    return True
