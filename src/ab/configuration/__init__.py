"""
Configuration

"""
from typing import Any

import yaml

import ab.configuration.yaml_constructors
from ab import pkg


_CONFIGURATION: dict[str, Any] = None


def load() -> Any:
    """
    Load built-in configuration file for AutoBernese.

    """
    global _CONFIGURATION
    if _CONFIGURATION is None:
        _CONFIGURATION = yaml.safe_load(pkg.configuration.read_text())
    return _CONFIGURATION
