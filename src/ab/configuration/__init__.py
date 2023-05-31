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
    if not keep_env:
        combined.pop("bsw_env")
        combined.pop("bsw_files")
        combined.pop("env")
        combined.pop("runtime")
    return combined


def _load() -> Any:
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


def load() -> Any:
    """
    Load built-in and user-supplied configuration files for AutoBernese.

    """
    global _CONFIGURATION
    if _CONFIGURATION is None:
        _CONFIGURATION = _load()
    return _CONFIGURATION
