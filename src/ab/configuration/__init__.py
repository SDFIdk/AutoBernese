"""
Read configuration files and set up the AutoBernese runtime environment.

AutoBernese contains a built-in configuration file, called the core
configuration. It contains settings needed for the package to function as
intended:

*   Know the environment variables that are set for the Bernese GNSS Software
    system [BSW]
*   Derive other settings from these variables in order to access BSW files and
    create and access files inside the AutoBernese runtime environment.

Users are supposed to extend the core configuration in two possible locations:
relative to the runtime directory and the active Bernese-campaign directory,
respectively; 'active' here indicating that only one campaign configuration file
may be used at the time.

Settings stored in the runtime directory are refered to as the common
configuration. Its purpose is to have a single place to keep settings shared
across all campaigns/actions.

Settings stored in a given campaign directory are referred to as a
campaign-specific configuration. A Bernese campaign directory must have a
campaign configuration file for the campaign to be run by AutoBernese.


The core configuration is always loaded by itself, since it is used to locate
the other configuration files. In addition, the configuration used by
AutoBernese for a specific action is based on the core configuration with
additions or overrides from the common configuration and, if relevant, a
campaign configuration.

If no common configuration file has been added by the users, and the action
performed requires no campaign-specific configuration, the primary configuration
is identical to the core configuration.

The core configuration is 'live' as long as the application runs, so that each
action can use it as base for its specific configuration.


A live configuration is obtained, when the static file content has been read,
parsed and converted to Python data structures. Many settings in the static
configuration file are abstract in that they are not 'seen' or 'known', until
they have been rendered by constructors in the format's parser: ISO-formatted
datestrings are automatically converted to date(time) instances, and integers,
floats and boolean-like values are also recognised and converted to their type.
In addition, special constructors are used to resolve environment variables from
the system, build file paths from path components, etc.


The format itself, YAML, allows duplicate keys at the same level, in that it
will override a previous key with its duplicate entry. In other words,
configuration 'sections' at the same nesting level override previous sections of
the same name, replacing the previous content with that of the later section.

Secondly, the YAML format allows the re-use of content by adding references to
earlier parts in the same document. The referenced content is still accessible
later on, even if it was located inside a 'section' that has been overriden
later on in that document. The references are not present, and thus not usable,
in the rendered configuration.


These rules of the format are relied on when building the configuration for an
action:

*   The core configuration used as base contains names of sections that may be
    overridden. It thus serves as a base configuration to be extended, and its
    settings define what parts of it that may be overridden, when creating
    another configuration from it.
*   Extending the core configuration is done by first merging the raw content of
    the core + common + campaign configuration files as needed.
*   References added to one file is then available for re-use in itself and
    configuration content in the next file.
*   The merged, static configuration is read by the YAML parser so that the
    references can be used. Here, any duplicate keys are overridden as allowed
    by the format.
*   Allowed settings from this stand-alone configuration are then extracted and
    combined with the base (i.e. core) to either add or update (override) the
    built-in settings.

This is the rendered configuration used by the given action in AutoBernese.

"""

from typing import (
    Final,
    Any,
)
from collections.abc import Iterable
from pathlib import Path
import getpass
import logging
import os
import functools

import yaml

from ab.configuration import constructors
from ab import pkg


constructors.add()

type ConfigurationType = dict[str, Any]

_POP: Final = {
    "bsw_env",
    "bsw_files",
    "env",
    "runtime",
    "campaign",
}
"Set of keys to remove from configuration, if so specified."


def loads(raw: str, /) -> ConfigurationType:
    """
    Load string input as a YAML document.

    NOTE:

    Repeated entries (key-value pairs) at the same nesting level in the raw text
    override previously defined entries, but YAML anchors defined in an
    overriden entry are still available.

    """
    return yaml.safe_load(raw)


def loadgps_setvar_sourced() -> bool:
    for key in pkg.bsw_env_vars.read_text().splitlines():
        if key not in os.environ:
            return False
    return True


@functools.cache
def _core() -> ConfigurationType:
    if not loadgps_setvar_sourced():
        raise SystemExit(
            "Please source `BERN54/LOADGPS.setvar` before running AutoBernese ..."
        )
    return loads(pkg.env.read_text())


def _runtime() -> dict[str, Any]:
    runtime = _core().get("runtime")
    if runtime is None:
        raise RuntimeError("No `runtime` section found ...")
    return runtime


def _common_config() -> Path:
    common_config = _runtime().get("common_config")
    if common_config is None:
        raise RuntimeError("No `common_config` sub section found ...")
    return Path(common_config)


def _campaign_templates() -> Path:

    campaign_templates = _runtime().get("campaign_templates")
    if campaign_templates is None:
        raise RuntimeError("No `campaign_templates` sub section found ...")

    directory = Path(campaign_templates)
    if not directory.is_dir():
        raise RuntimeError(
            "Campaign template directory {directory!r} does not exist ..."
        )

    return directory


def _sections_to_override() -> list[str]:
    sections_to_override = _runtime().get("sections_to_override")
    if sections_to_override is None:
        raise RuntimeError("No `sections_to_override` sub section found ...")
    return sections_to_override


def merge(*filenames: Path | str) -> str:
    """
    Merge file contents in the order of the given filenames.

    Duplicate file references are removed.

    Raises a RuntimeError, if a file does not exist.

    Returns an empty string, if no files are given.

    """
    # Using a list to keep the order
    unique = []
    for fname in filenames:
        ifname = Path(fname).absolute()
        if not ifname.is_file():
            raise RuntimeError(f"File {ifname} does not exist ...")
        if ifname in unique:
            continue
        unique.append(ifname)
    fstr = "\n".join("{}" for _ in range(len(unique)))
    contents = (ifname.read_text() for ifname in unique)
    return fstr.format(*contents)


def update(
    raw: ConfigurationType, /, *, base: ConfigurationType = _core()
) -> ConfigurationType:
    """
    Update `base` configuration with allowed sections from the `raw`
    configuration. Allowed sections are defined in the core configuration which
    is pre-loaded to obtain this information.

    """
    if not isinstance(base, dict):
        raise TypeError(f"Configuration is not a dictionary ...")

    if not isinstance(raw, dict):
        return base

    overrides = {
        section: raw.get(section)
        for section in _sections_to_override()
        if section in raw
    }
    return {**base, **overrides}


def clean(
    config: ConfigurationType, spare: Iterable[str] | None = None, /
) -> ConfigurationType:
    """
    Remove keys from configuration unless spared by the optional argument.

    """
    popable = _POP
    if spare is not None:
        popable -= set(spare)
    for key in popable:
        config.pop(key)
    return config


@functools.cache
def load(
    *args: Path | str,
    use_common: bool = True,
    keep_env: bool = False,
    keys_spared: Iterable[str] | None = None,
) -> ConfigurationType:
    """
    Extend core + common configuration with given configuration file(s) allowing
    the re-use of settings stored in the core and/or common configuration files.

    It returns an extended core configuration with allowed sections added or
    overridden.

    Files are concatenated with the content of the core and common configuration
    files and load as a single configuration. This is then used as the source of
    updates to the core configuration.

    By default, some core settings are removed from the returned configuration,
    if a filename is supplied, since users would find them noisy, when viewing
    e.g. a rendered campaign configuration. And from an API-point of view, they
    should not be needed, after the references have been re-used during the
    construction.

    """
    # Core
    filenames: list[Path | str] = [pkg.env]

    # Common
    ifname_common = _common_config()
    if use_common and ifname_common.is_file():
        filenames.append(ifname_common)

    # Campaign (or other)
    filenames.extend(args)

    # Load them as one configuration file.
    raw = loads(merge(*filenames))

    # Only add/override allowed keys in core configuration
    updated = update(raw)

    # Remove core settings or not
    if keep_env or not args:
        return updated

    return clean(updated, keys_spared)


def set_up_runtime_environment():
    """
    For the command-line application, but might also be needed if using the
    package API directly.

    """
    # Create runtime directory
    runtime = _runtime()
    runtime.get("ab").mkdir(exist_ok=True)

    # Configure logging

    # Get the basic arguments for log configuration
    log_settings = runtime.get("logging")

    # Create log file if not existing
    log_settings.get("filename").touch()

    # Add current username to log format string
    parameters = dict(user=getpass.getuser())
    template = log_settings.get("format")
    log_settings["format"] = template.format(**parameters)
    logging.basicConfig(**log_settings)
