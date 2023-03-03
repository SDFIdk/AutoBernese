"""
Configuration

"""
import pathlib
from importlib import (
    resources,
)
from typing import Any

import yaml
from yaml_env_tag import construct_env_tag

import ab

yaml.SafeLoader.add_constructor("!ENV", construct_env_tag)

ifname_default = resources.files(ab).joinpath("autobernese.yaml")


def load(fname: str | pathlib.Path = ifname_default) -> Any:
    """
    Load built-in configuration file for AutoBernese.

    """
    ifname = pathlib.Path(fname)
    if not ifname.is_file():
        raise LookupError(f"Configuration file {ifname} does not exist ...")
    return yaml.safe_load(ifname.read_text())
