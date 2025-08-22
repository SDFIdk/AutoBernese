import datetime as dt
from dataclasses import dataclass


@dataclass
class SiteIdentificationOfTheGNSSMonument:
    site_name: str
    four_character_id: str
    nine_character_id: str | None
    domes: str
    date_installed: str


@dataclass
class SiteLocationInformation:
    city_or_town: str
    country: str


@dataclass
class GNSSReceiverInformation:
    receiver_type: str
    receiver_serial_number: str
    firmware: str
    date_installed: str
    date_removed: str


@dataclass
class GNSSAntennaInformation:
    antenna_type: str
    antenna_serial_number: str
    marker_up: str
    marker_north: str
    marker_east: str
    date_installed: str
    date_removed: str
