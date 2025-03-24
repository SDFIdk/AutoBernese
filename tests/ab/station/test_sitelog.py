from pathlib import Path

from ab.station.sitelog import Sitelog


def test_sitelog_parsing():
    # https://www.epncb.oma.be/ftp/station
    dirs = Path(__file__).parent.glob("log*")
    ifnames = []
    for directory in dirs:
        ifnames.extend(directory.glob("*.log"))
    for ifname in ifnames:
        # Instance opens provided file and parses it
        # It will fail, when not working.
        try:
            expected = ifname.name[: ifname.name.find("_")].upper()
            sitelog = Sitelog(ifname)
        except Exception as e:
            assert False, f"Error reading {ifname.name!r} ..."
        result = sitelog.section_1.get("four_character_id").upper()
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."
