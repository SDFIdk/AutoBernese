"""
Work with Bernese campaigns in the current Bernese environment

"""

import os
import datetime as dt
import getpass
from typing import (
    Any,
    Final,
)
from dataclasses import (
    dataclass,
    asdict,
    field,
)
from pathlib import Path
from string import Template
import shutil
import logging

import ab
from ab import (
    pkg,
    configuration,
)
from ab.data.stats import dir_size


log = logging.getLogger(__name__)


CONFIG_NAME: Final = "campaign.yaml"


def template_dir() -> Path:
    """
    Return the Path instance to the directory containing the campaign templates.

    """
    return configuration._campaign_templates()


def bsw_env() -> dict[str, str | Path]:
    """
    Return dictionary with the current Bernese installation environment relevant
    to AutoBernese.

    """
    return configuration.load().get("bsw_env", {})


def project_dir() -> Path:
    """
    Return path to campaign-directory container `$P`

    """
    return Path(bsw_env().get("P", ""))


def bsw_files() -> dict[str, str | Path]:
    """
    Return dictionary with Bernese file paths relevant to AutoBernese.

    """
    return configuration.load().get("bsw_files", {})


def campaign_menu_file() -> Path:
    """
    Return path to the campaign-menu file inside the Bernese installation

    """
    return Path(bsw_files().get("campaign_menu", ""))


_TEMPLATE_P: Final = r"${P}"
"""
The shell/perl-friendly string representing the environment variable $P used by
Bernese GNSS Software to point to the campaign directory.
"""


@dataclass
class MetaData:
    """
    Model for the metadata section in campaign configuration file

    """

    campaign: str
    template: str
    beg: str | dt.datetime
    end: str | dt.datetime
    version: str = ab.__version__
    created: str | dt.datetime = dt.date.today().isoformat()
    username: str = getpass.getuser()


def init_template_dir() -> None:
    """
    Create campaign-template directory in AutoBernese runtime directory.

    Does nothing if the template directory already exists.

    Otherwise, create it and add the built-in default template.

    """
    path = template_dir()
    if path.is_dir():
        return

    log.info(f"Create campaign-template directory {path} ...")
    path.mkdir(exist_ok=True, parents=True)

    log.info(
        f"Copy default template-campaign configuration {pkg.template_campaign_default} to {path} ..."
    )
    shutil.copy(str(pkg.template_campaign_default), str(path))


def available_templates() -> list[str]:
    """
    Return list of available campaign templates.

    """
    return [fname.stem for fname in template_dir().glob("*.yaml")]


def read_template(name: Path | str) -> str:
    if not name in available_templates():
        raise ValueError(f"Template {name!r} does not exist ...")
    ifname = (template_dir() / name).with_suffix(".yaml")
    return ifname.read_text()


def _extract_campaign_list(raw: str) -> list[str]:
    """
    Reads the list of existing campaign directories from a string matching
    possible content in the file `MENU_CMP.INP` in the current Bernese
    installation directory.

    The full path to each campaign directory is resolved using the given
    environment variables.

    """
    meat = raw.split("  ## widget")[0]
    meat = meat.split("CAMPAIGN ")[1]
    meat = meat.split(maxsplit=1)[1].strip()
    lines = [item.strip() for item in meat.splitlines()]
    # Use Template instance to avoid security leaks.
    return [Template(s).safe_substitute(bsw_env()).strip('"') for s in lines]


@dataclass
class CampaignInfo:
    """
    Container for campaign information

    """

    directory: str
    size: float = 0
    template: str = ""
    version: str = ""
    username: str = ""
    created: str = ""


def ls(verbose: bool = False) -> list[CampaignInfo]:
    """
    Return list of existing Bernese campaigns.

    Calculate directory size and display metadata, if `verbose is True`.

    """
    result = [
        CampaignInfo(path)
        for path in _extract_campaign_list(campaign_menu_file().read_text())
    ]
    if not verbose:
        return result

    for campaign_info in result:
        campaign_info.size = dir_size(campaign_info.directory)
        ifname = Path(campaign_info.directory) / CONFIG_NAME
        if not ifname.is_file():
            continue
        meta = configuration.load(ifname).get("metadata", {})
        for key, value in meta.items():
            setattr(campaign_info, key, value)

    return result


def campaign_dir(name: str) -> Path:
    """
    Return the directory path to the campaign `name`.

    """
    return project_dir() / f"{name}"


def _campaign_config(name: str) -> Path:
    """
    Return the configuration-file path to the campaign `name`.

    """
    return campaign_dir(name) / CONFIG_NAME


def subdirectories(name: str) -> dict[str, str]:
    """
    Get actual subdirectories directly beneath campaign directory.

    """
    return {p.name: p.path for p in os.scandir(campaign_dir(name)) if p.is_dir()}


def just_load(name: str) -> dict[str, Any]:
    """
    Load configuration for given campaign name without side effects.

    """
    return configuration.load(_campaign_config(name))


def set_environment_variables(changes: list[dict[str, Any]]) -> None:
    """
    Set environment variables, overriding any existing ones.

    Invalid variable names are skipped.

    """
    if not isinstance(changes, list):
        log.debug("Expected list instance, got {changes!r} ...")
        return

    for change in changes:
        variable = change.get("variable")
        if not (s := str(variable)) == variable or s.strip() != s or s.split()[0] != s:
            log.debug(
                f"Only a single-word string is acceptable as variable name. Got {variable!r} ..."
            )
            continue
        value = str(change.get("value"))
        os.environ[variable] = value


def load(name: str) -> dict[str, Any]:
    """
    Load configuration for given campaign name and change environment variables
    if the setting exists.

    """
    c = just_load(name)
    if (changes := c.get("environment")) is not None:
        set_environment_variables(changes)
    return c


def create_campaign_configuration_file(metadata: MetaData) -> None:
    """
    Create campaign-configuration file in the campaign directory

    """
    ofname = _campaign_config(metadata.campaign)
    log.info(f"Creating campaign-configuration file {ofname} ...")
    header = pkg.campaign_header.read_text().format(**asdict(metadata))
    template = read_template(metadata.template)
    ofname.write_text(f"{header}\n{template}")


def build_campaign_directory_tree(name: str) -> None:
    """
    Read the campaign directory tree settings from the configuration, make
    directories and copy selected files.

    Files not existing are skipped.

    """
    path = campaign_dir(name)
    if not path.is_dir():
        log.debug(f"Campaign directory {path!r} is not a directory ...")
        return

    # Load configuration with campaign directory tree settings spared.
    keys_spared = ("campaign",)
    c = configuration.load(_campaign_config(name), keys_spared=keys_spared)
    # (Alternatively, calling conaifuration.load() without the campaign config
    # file path, the setting will also be spared.)
    directories = c.get("campaign", {}).get("directories")

    if directories is None:
        msg = f"List of campaign directories to create is empty ..."
        log.error(msg)
        raise RuntimeError(msg)

    # Create required campaign-directory tree
    log.info(f"Create required campaign-directory tree ...")
    for directory_info in directories:
        # Validation
        directory_name = directory_info.get("name")
        if directory_name is None:
            log.warning(
                f"No directory name given with directory info {directory_info!r} ..."
            )
            continue

        # We are creating a new directory in an existing one
        path_full = campaign_dir / directory_name
        path_full.mkdir()

        # Any specified file paths are copied over to the new directory
        for fname_source in directory_info.get("files", []):
            # Source-file validation
            ifname_source = Path(fname_source)
            if not ifname_source.is_file():
                log.warning(f"Source file {fname_source} does not exist ...")
                continue

            log.info(f"Copy {fname_source} to {directory_name} ...")
            shutil.copy(fname_source, path_full / ifname_source.name)


def build_campaign_menu(campaign_names: list[str]) -> str:
    """
    Build content for a MENU_CMP.INP file with list of the given campaigns.

    If a campaign path matches that of the default Bernese campaign-directory
    container denoted `${P}`, the respective path component is replaced with
    these literals.

    """
    # Replace full paths to short-hand paths
    _P = str(project_dir())
    formatted: list[str] = [
        f'  "{campaign.replace(_P, _TEMPLATE_P)}"' for campaign in campaign_names
    ]
    count = len(campaign_names)
    separator = "\n" if count > 1 else ""
    campaigns = "\n".join(formatted)
    parameters = dict(count=count, separator=separator, campaigns=campaigns)
    return pkg.template_campaign_menu_list.read_text().format(**parameters)


def add_campaign_to_bsw_menu(name: str) -> None:
    """
    Update the campaign-menu file in Bernese install directory.

    Resolve campaign-directory path and add it to the list of campaigns in the
    campaign-menu file in the Bernese-installation directory.

    """
    path = campaign_dir(name)
    if not path.is_dir():
        msg = f"Campaign directory {path!r} is not a directory ..."
        log.warn(msg)
        return

    # Load existing campaign-menu file
    campaign_menu = campaign_menu_file()
    raw = campaign_menu.read_text()

    # Create a backup file just as Bernese does
    # This might be unnecessary, but, for now, we just mimic its behaviour
    campaign_menu.with_suffix(".bck").write_text(raw)

    # Update the campaign list

    # Put existing Bernese campaign paths into a set to get unique paths
    existing = set(_extract_campaign_list(raw))

    # Add new path to this set and sort updates to get a list
    updated = sorted(existing | {f"{path}"})

    # Write the formatted updates to the original campaign-menu file
    campaign_menu.write_text(build_campaign_menu(updated))


def create(name: str, template: str, beg: dt.date, end: dt.date) -> None:
    """
    Create a campaign.

    """
    # Store the intention
    log.info(f"Creating campaign with the following input:")
    log.info(f"{name=}")
    log.info(f"{template=}")
    log.info(f"{beg=}")
    log.info(f"{end=}")

    # Validate

    # Does the campaign already exist?
    path = campaign_dir(name)
    if path.is_dir():
        msg = f"Campaign directory {path} exists ..."
        log.warn(msg)
        return

    # Is the template available?
    if template not in available_templates():
        msg = f"Template {template} does not exist ..."
        log.warn(msg)
        return

    # Create

    # Create campaign directory
    log.info(f"Creating campaign directory {path} ...")
    path.mkdir(parents=True)

    # Create campaign configuration file with runtime metadata
    metadata = MetaData(
        username=getpass.getuser(),
        template=template,
        campaign=name,
        beg=beg.isoformat(),
        end=end.isoformat(),
    )
    create_campaign_configuration_file(metadata)

    # Create campaign directory
    build_campaign_directory_tree(name)

    # Make campaign visible in Bernese campaign menu
    add_campaign_to_bsw_menu(name)
