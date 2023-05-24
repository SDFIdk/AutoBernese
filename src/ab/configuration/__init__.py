"""
Configuration

"""
from typing import (
    Any,
    Iterable,
)
from pathlib import Path

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


def merge(*filenames: Iterable[Path | str]) -> str:
    """
    Merge file contents in the order of the given filenames.

    """
    fstr = "{}\n" * len(filenames)
    contents = (Path(ifname).read_text() for ifname in filenames)
    return fstr.format(*contents)


def with_bsw_env(ifname: Path | str, *, keep_env: bool = True) -> dict[str, Any]:
    """
    Combine file with BSW environment and load as a single YAML document.

    """
    combined = yaml.safe_load(merge(pkg.env, ifname))
    if not keep_env:
        combined.pop("bsw_env")
    return combined
