"""
Configuration

"""
from typing import Any
import pathlib
import os

import yaml
from yaml_env_tag import construct_env_tag

from ab import pkg


yaml.SafeLoader.add_constructor("!ENV", construct_env_tag)

_CONFIGURATION: Any = None


def load() -> Any:
    """
    Load built-in configuration file for AutoBernese.

    """
    global _CONFIGURATION

    if _CONFIGURATION is not None:
        return _CONFIGURATION

    ifname = pathlib.Path(pkg.configuration)
    if not ifname.is_file():
        raise LookupError(f"Configuration file {ifname} does not exist ...")

    _CONFIGURATION = yaml.safe_load(ifname.read_text())
    return _CONFIGURATION
