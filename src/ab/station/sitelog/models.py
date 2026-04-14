import datetime as dt
from dataclasses import dataclass, fields

SITELOG_DEFAULTS = {
    "domes": "(A9)",
    "receiver_serial_number": "(A20, but note the f",
    "firmware": "(A11)",
    "antenna_serial_number": "(A*, but note the first A5 is used in SINEX)",
}

DESIRED_DEFAULTS = {
    "domes": "",
    "receiver_serial_number": "",
    "firmware": "",
    "antenna_serial_number": "",
}


class SitelogSection:
    def __post_init__(self):
        for field in fields(self):
            if (
                field.name in SITELOG_DEFAULTS.keys()
                and getattr(self, field.name) == SITELOG_DEFAULTS[field.name]
            ):
                setattr(self, field.name, DESIRED_DEFAULTS.get(field.name, ""))


@dataclass
class SiteIdentificationOfTheGNSSMonument(SitelogSection):
    site_name: str
    four_character_id: str
    nine_character_id: str | None
    domes: str
    date_installed: str


@dataclass
class SiteLocationInformation(SitelogSection):
    city_or_town: str
    country: str


@dataclass
class GNSSReceiverInformation(SitelogSection):
    receiver_type: str
    receiver_serial_number: str
    firmware: str
    date_installed: str
    date_removed: str


@dataclass
class GNSSAntennaInformation(SitelogSection):
    antenna_type: str
    antenna_serial_number: str
    marker_up: str
    marker_north: str
    marker_east: str
    azimuth: str
    date_installed: str
    date_removed: str
