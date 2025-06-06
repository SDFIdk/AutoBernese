import datetime as dt
from dataclasses import dataclass

from string import Template
from typing import Any


@dataclass
class BPETerminalOutput:
    """
    Container for result printed in the terminal:

    """

    beg: dt.datetime
    username: str
    pcf_file: str
    cpu_file: str
    campaign: str
    year_session: str
    output_file: str
    status_file: str
    end: dt.datetime
    server_pid: str = "UNKNOWN"
    ok: bool = True


def parse_bpe_terminal_output(
    raw: str, substitutes: dict[str, str] | None = None
) -> BPETerminalOutput:
    if substitutes is not None:
        raw = Template(raw).safe_substitute(substitutes)
    lines = [line.strip() for line in raw.splitlines() if line.strip() != ""]
    fmt = "%d-%b-%Y %H:%M:%S"
    results: dict[str, Any] = {}
    for line in lines:
        if line.startswith("Starting BPE on "):
            results["beg"] = dt.datetime.strptime(line[-20:], fmt)
            continue
        if line.endswith("@"):
            results["username"] = line[:-1]
            continue
        if line.startswith("PCFile:"):
            results["pcf_file"] = line.split("PCFile:")[-1].strip()
            continue
        if line.startswith("CPU file:"):
            results["cpu_file"] = line.split("CPU file:")[-1].strip()
            continue
        if line.startswith("Campaign:"):
            results["campaign"] = line.split("Campaign:")[-1].strip()
            continue
        if line.startswith("Year/session:"):
            results["year_session"] = line.split("Year/session:")[-1].strip()
            continue
        if line.startswith("BPE output:"):
            results["output_file"] = line.split("BPE output:")[-1].strip()
            continue
        if line.startswith("BPE status:"):
            results["status_file"] = line.split("BPE status:")[-1].strip()
            continue
        if line.startswith("BPE server runs PID ="):
            results["server_pid"] = line.split("BPE server runs PID =")[-1].strip()
            continue
        if line.startswith("BPE finished") or line.startswith("BPE error"):
            results["end"] = dt.datetime.strptime(line[-20:], fmt)
            continue
        if line.startswith("User script error"):
            results["ok"] = False
    return BPETerminalOutput(**results)
