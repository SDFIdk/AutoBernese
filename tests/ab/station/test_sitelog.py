from pathlib import Path

from ab.station.sitelog import Sitelog


def test_sitelog_parsing():
    # https://www.epncb.oma.be/ftp/station
    # dirs = Path(__file__).parent.glob("log*")  # Use this, when support for sitelog version 2 is supported.
    dirs = [Path(__file__).parent / "log"]
    ifnames = []
    for directory in dirs:
        ifnames.extend(directory.glob("*.log"))
    for ifname in ifnames:
        # Instance opens provided file and parses it
        # It will fail, when not working.
        try:
            sitelog = Sitelog(ifname)
        except Exception as e:
            assert False, f"Error reading {ifname.name!r} ..."
