"""
Custom PyYAML constructors

"""

from yaml.loader import SafeLoader
from yaml_env_tag import construct_env_tag  # type: ignore

from ab.configuration.constructors import (
    paths,
    dates,
)


_tag_constructor_map = (
    # Read environment variables
    ("!ENV", construct_env_tag),
    # Build paths
    ("!Path", paths.path_constructor),
    ("!PathStr", paths.path_as_str_constructor),
    ("!Parent", paths.parent_constructor),
    # Use parameters
    ("!DateRange", dates.date_range_constructor),
    ("!AsGPSDate", dates.date_to_gps_date_constructor),
)


def add():
    for tag, constructor in _tag_constructor_map:
        SafeLoader.add_constructor(tag, constructor)

    # Make all timestamps GPSDate instances
    tag = "tag:yaml.org,2002:timestamp"
    timestamp_constructor = SafeLoader.yaml_constructors[tag]
    wrapped_timestamp_constructor = dates.timestamp2GPSDate(timestamp_constructor)
    SafeLoader.yaml_constructors[tag] = wrapped_timestamp_constructor
