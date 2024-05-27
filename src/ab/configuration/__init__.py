"""
Configuration

"""

from typing import (
    Final,
    Any,
    Iterable,
)
from pathlib import Path
import getpass
import logging
import os

import yaml

import ab.configuration.yaml_constructors
from ab import pkg


_CONFIGURATION: dict[str, Any] = None
_POP: Final = (
    "bsw_env",
    "bsw_files",
    "env",
    "runtime",
    "campaign",
)


def clean(config: dict[str, Any]) -> dict[str, Any]:
    for key in _POP:
        config.pop(key)
    return config


def merge(*filenames: Iterable[Path | str]) -> str:
    """
    Merge file contents in the order of the given filenames.

    """
    fstr = "{}\n" * len(filenames)
    contents = (Path(ifname).read_text() for ifname in filenames)
    return fstr.format(*contents)


def with_env(ifname: Path | str, *, keep_env: bool = False) -> dict[str, Any]:
    """
    Combine file with pre-defined environment and load as a single YAML
    document.

    """
    combined = yaml.safe_load(merge(pkg.env, ifname))
    if keep_env:
        return combined
    return clean(combined)


def _load() -> dict[str, Any]:
    """
    Actual loader of the AutoBernese configuration file.

    First the package-supplied configuration is loaded, and if a user-defined
    configuration file is present in the AutoBernese runtime directory, the
    allowed sections are updating the already-loaded configuration.

    """
    env = yaml.safe_load(pkg.env.read_text())
    user_config = env.get("runtime").get("user_config")
    if user_config is not None and (ifname := Path(user_config)).is_file():
        user_sections = env.get("runtime").get("user_sections")
        updates_proposed = yaml.safe_load(merge(pkg.env, ifname))
        updates = {
            key: updates_proposed.get(key)
            for key in user_sections
            if key in updates_proposed
        }
        env.update(updates)
    return env


def load() -> dict[str, Any]:
    """
    Load built-in and user-supplied configuration files for AutoBernese.

    """
    global _CONFIGURATION
    if _CONFIGURATION is None:
        _CONFIGURATION = _load()
    return _CONFIGURATION


LOADGPS_setvar: Final = (
    "VERSION",
    "F_VERS",
    "F_VERS_LIST",
    "C",
    "SRC",
    "LG",
    "FG",
    "XG",
    "XQ",
    "SPT",
    "BPE",
    "EXE",
    "SUP",
    "DOC",
    "HLP",
    "PAN",
    "GLOBAL",
    "MODEL",
    "CONFIG",
    "USR",
    "OPT",
    "PCF",
    "SCR",
    "BPE_SERVER_HOST",
    "U",
    "T",
    "P",
    "D",
    "S",
    "QTBERN",
    "OS",
    "OS_NAME",
    "CGROUP",
)


def LOADGPS_setvar_sourced() -> bool:
    for key in LOADGPS_setvar:
        if key not in os.environ:
            return False
    return True


def set_up_runtime_environment():
    """For the command-line application"""
    runtime = load().get("runtime")
    runtime.get("ab").mkdir(exist_ok=True)
    log_kw = runtime.get("logging")
    log_kw.get("filename").touch()
    replacements = dict(
        format=log_kw.get("format").format(user=getpass.getuser()),
    )
    logging.basicConfig(**{**log_kw, **replacements})
