from enum import Enum
from pathlib import Path
import logging

from ab.station.sitelog.parse import (
    parse_sections,
    parse_section_1,
    parse_section_2,
    parse_subsection_3,
    parse_subsection_4,
)


log = logging.getLogger(__name__)


class StationIDLength(Enum):
    FOUR = "four"
    NINE = "nine"

    @classmethod
    def values(self) -> list[str]:
        return [item.value for item in self]


station_id_keys = {
    StationIDLength.FOUR: "four_character_id",
    StationIDLength.NINE: "nine_character_id",
}
"Mapping between enum and sitelog dict key with the chosen ID format"


class Sitelog:
    """
    Sitelog reads given filename and stores parsed sitelog data.

    """

    def __init__(
        self,
        filename: Path | str,
        preferred_station_id_length: str | None = None,
    ) -> None:

        self.filename = Path(filename)

        # Validate

        try:
            sitelog_content = self.filename.read_text()

        except Exception as e:
            log.warning(f"Caught error {e!r}, when reading file {self.filename!r} ...")
            sitelog_content = self.filename.read_text(encoding="cp1252")

        # Choose preferred station ID, if choice is available
        chosen: StationIDLength | None = None
        if preferred_station_id_length is not None:
            try:
                chosen = StationIDLength(preferred_station_id_length)
            except ValueError as e:
                expected = StationIDLength.values()
                part_1 = f"Expected `station_id_characters` to be in {expected!r}."
                part_2 = f"Got {preferred_station_id_length!r} ..."
                log.error(f"{part_1} {part_2}")
                log.info("Using largest ID length in each individual sitelog ...")

        # Extract raw section contents
        self.sections = parse_sections(sitelog_content)

        # Build model structure
        self.section_1 = parse_section_1(self.sections["1"]["content"])
        self.section_2 = parse_section_2(self.sections["2"]["content"])
        self.receivers = [
            parse_subsection_3(subsection)
            for subsection in self.sections["3"]["subsections"]
        ]
        self.antennae = [
            parse_subsection_4(subsection)
            for subsection in self.sections["4"]["subsections"]
        ]

        # Derived station ID
        # ------------------

        # Here, the parsing has mixed v1 and v2 of the sitelog format that
        # changed ~ 2024. Version 1 provides four, and not nine, and vice versa.
        four = self.section_1.four_character_id
        nine = self.section_1.nine_character_id

        # Make it possible to prefer four-letter ID, when nine (and thus not
        # four) was found by setting four to the first characters in the
        # nine-letter ID.
        if nine is not None:
            nine = nine.upper()
            four = nine[:4]

        # If no valid preferred length is chosen, use longest ID supported by
        # the sitelog
        if chosen is None:
            if nine is not None:
                self.station_id = nine
            else:
                self.station_id = four
            return

        # If preferred length is nine
        if chosen is StationIDLength.NINE:
            if nine is not None:
                self.station_id = nine
                return
            else:
                log.warning(
                    f"Chosen station-ID length is nine, but {self.filename.name} does not have nine."
                )

        # The only other option so far is StationIDLength.FOUR, but as this is
        # also the default, we log it as such.
        #
        # Default to the four-letter one which is assumed to always exist
        log.info(f"Using four-letter station name {four} as station ID.")
        self.station_id = four

    def save_sections_raw(self, ofname: Path | str) -> None:
        ofname = Path(ofname)
        with open(ofname, "w+") as f:
            json.dump(self.sections, f, indent=2)

    @property
    def sections_extracted(self) -> dict[str, str]:
        return dict(
            sec1=asdict(self.section_1),
            sec2=asdict(self.section_2),
            sec3=[asdict(receiver) for receiver in self.receivers],
            sec4=[asdict(antenna) for antenna in self.antennae],
        )

    def save_sections_extracted(self, ofname: Path | str) -> None:
        ofname = Path(ofname)
        with open(ofname, "w+") as f:
            json.dump(self.sections_extracted, f, indent=2)
