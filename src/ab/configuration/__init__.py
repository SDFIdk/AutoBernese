"""
Configuration

"""
from typing import Any
import pathlib

import yaml

import ab.configuration.yaml_constructors
from ab import pkg


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
