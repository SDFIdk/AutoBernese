from pathlib import Path

from ab.station.sitelog import Sitelog

# https://www.epncb.oma.be/ftp/station


def test_sitelog_parsing_with_default_four_id_characters():
    directory = Path(__file__).parent / "log"
    ifnames = directory.glob("*.log")
    for ifname in ifnames:
        # Instance opens provided file and parses it
        # It will fail, when not working.
        expected = ifname.name[: ifname.name.find("_")].upper()
        "Station_ID from the filename (ignoring the modification date) in uppercase"
        try:
            sitelog = Sitelog(ifname)
        except Exception as e:
            assert False, f"Error reading {ifname.name!r} ..."

        four_character_id = sitelog.section_1.four_character_id
        assert (
            four_character_id is not None
        ), f"Expected to find `four_character_id` in {ifname} ..."

        result = four_character_id.upper()
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_sitelog_parsing_with_nine_id_characters():
    directory = Path(__file__).parent / "log_9char"
    ifnames = directory.glob("*.log")
    for ifname in ifnames:
        # Instance opens provided file and parses it
        # It will fail, when not working.
        expected = ifname.name[: ifname.name.find("_")].upper()
        "Station_ID from the filename (ignoring the modification date) in uppercase"
        try:
            sitelog = Sitelog(ifname, preferred_station_id_length="nine")
        except Exception as e:
            assert False, f"Error reading {ifname.name!r}. Got {e.__class__}: {e} ..."

        nine_character_id = sitelog.section_1.nine_character_id
        assert (
            nine_character_id is not None
        ), f"Expected to find `nine_character_id` in {ifname} ..."

        result = nine_character_id  # .upper()
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."
