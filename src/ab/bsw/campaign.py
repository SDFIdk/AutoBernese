"""
Module for working with campaigns in the current BSW environment.

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


def get_template_dir() -> Path:
    """
    Return the Path instance to the directory containing the campaign templates.

    """
    c = configuration.load()
    runtime = c.get("runtime")
    if not runtime:
        raise RuntimeError("Configuration must have a `runtime` section ...")
    templates = runtime.get("campaign_templates")
    if not templates:
        raise ValueError(
            "Configuration section m`runtime` has no value `campaign_templates` ..."
        )
    return Path(templates)


def get_bsw_env() -> dict[str, str | Path]:
    """
    Return dictionary with the current Bernese installation environment relevant
    to AutoBernese.

    """
    return configuration.load().get("bsw_env", {})


def get_campaign_dir() -> Path:
    """
    Return Path instance to the campaign directory `$P`.

    """
    return Path(get_bsw_env().get("P", ""))


def get_campaign_menu_file() -> Path:
    """
    Return Path instance pointing to the campaign menu inside the Bernese
    installation.

    """
    c = configuration.load()
    return Path(c.get("bsw_files", {}).get("campaign_menu"))


_TEMPLATE_P: Final = "${P}"
"""
The shell/pearl friendly string representing the environment variable $P used by
BSW to point to the campaign directory.
"""


@dataclass
class MetaData:
    """
    Model for the metadata section of a concrete campaign-specific configuration
    file.

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
    Create a directory for user-defined campaign templates in the autobernese
    directory.

    Does nothing if the template directory already exists.

    If it does not exist, the directory is created and the packaged default
    template is added.

    """
    template_dir = get_template_dir()
    if template_dir.is_dir():
        return

    log.info(f"Create campaign-template directory in {template_dir} ...")
    template_dir.mkdir(exist_ok=True, parents=True)

    log.info(
        f"Copy default template-campaign configuration {pkg.template_campaign_default} to {template_dir} ..."
    )
    shutil.copy(str(pkg.template_campaign_default), str(template_dir))


def available_templates() -> list[str]:
    """
    Return list of available campaign templates.

    """
    template_dir = get_template_dir()
    return [fname.stem for fname in template_dir.glob("*.yaml")]


def load_template(template: Path | str) -> str:
    if not template in available_templates():
        raise ValueError(f"Template {template!r} does not exist ...")
    ifname = (get_template_dir() / template).with_suffix(".yaml")
    return ifname.read_text()


def _extract_campaign_list(raw: str) -> list[str]:
    """
    Reads the list of existing campaign directories from a string matching
    possible content in the file `MENU_CMP.INP` in the current Bernese
    installation directory.

    """
    meat = raw.split("  ## widget")[0]
    meat = meat.split("CAMPAIGN ")[1]
    meat = meat.split(maxsplit=1)[1].strip()
    lines = [item.strip() for item in meat.splitlines()]
    # Use Template instance to avoid security leaks.
    return [Template(s).safe_substitute(get_bsw_env()).strip('"') for s in lines]


@dataclass
class CampaignInfo:
    directory: str
    size: float = 0
    template: str = ""
    version: str = ""
    username: str = ""
    created: str = ""


def ls(verbose: bool = False) -> list[CampaignInfo]:
    """
    Return list of created campaigns.

    """
    result = [
        CampaignInfo(path)
        for path in _extract_campaign_list(get_campaign_menu_file().read_text())
    ]
    if not verbose:
        return result

    for campaign_info in result:
        campaign_info.size = dir_size(campaign_info.directory)
        ifname = Path(campaign_info.directory) / "campaign.yaml"
        if not ifname.is_file():
            continue
        meta = configuration.with_env(ifname).get("metadata", {})
        for key, value in meta.items():
            setattr(campaign_info, key, value)

    return result


def _campaign_dir(name: str) -> Path:
    """
    Return the directory path to the campaign `name`.

    """
    return get_campaign_dir() / f"{name}"


def _campaign_configuration(name: str) -> Path:
    """
    Return the configuration-file path to the campaign `name`.

    """
    return _campaign_dir(name) / "campaign.yaml"


def build_campaign_menu(campaign_list: list[str]) -> str:
    """
    Build content for a MENU_CMP.INP file with list of the given campaigns.

    If a campaign path matches that of the default Bernese campaign directory
    denoted `${P}`, the respective path component is replaced with these
    literals.

    """
    _P = str(get_campaign_dir())
    formatted: list[str] = [
        f'  "{campaign.replace(_P, _TEMPLATE_P)}"' for campaign in campaign_list
    ]
    count: int = len(campaign_list)
    separator: str = "\n" if count > 1 else ""
    campaigns: str = "\n".join(formatted)
    parameters = dict(count=count, separator=separator, campaigns=campaigns)
    return pkg.template_campaign_menu_list.read_text().format(**parameters)


def add_campaign_to_bsw_menu(path: str | Path) -> None:
    """
    Update the campaign-menu file in Bernese install directory.

    Add given campaign path to the list of campaigns in the campaign-menu file
    in the Bernese installation directory.

    """
    path = Path(path)
    if not path.is_dir():
        raise ValueError(f"Path {path!r} is not a directory ...")

    campaign_menu = get_campaign_menu_file()

    # Load existing campaign-menu file
    raw = campaign_menu.read_text()

    # Create a backup just as BSW does.
    campaign_menu.with_suffix(".bck").write_text(raw)

    # Update the campaign list
    existing = set(_extract_campaign_list(raw))

    # We convert the PosixPath to a string, and the make a single-element set
    # with that string before adding it to the existing list and sorting it.
    updated = sorted(existing | {f"{path}"})

    # Write the updated and formatted list to the campaign-menu file.
    campaign_menu.write_text(build_campaign_menu(updated))


def build_campaign_directory_tree(campaign_dir: Path | str) -> None:
    campaign_dir = Path(campaign_dir)
    directories = configuration.load().get("campaign", {}).get("directories")

    if directories is None:
        msg = f"list of campaign directories to create is empty in the user configuration ..."
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


def create_campaign_configuration_file(
    campaign_dir: Path | str, metadata: MetaData
) -> None:
    """
    Create a campaign configuration file with relevant metadata.

    """
    campaign_dir = Path(campaign_dir)
    if not campaign_dir.is_dir():
        msg = f"{campaign_dir!r} is not a directory ..."
        log.error(msg)
        raise RuntimeError(msg)

    # Create AutoBernese campaign-configuration file
    fname_campaign_config = campaign_dir / "campaign.yaml"
    log.info(
        f"Creating AutoBernese campaign-configuration file {fname_campaign_config} ..."
    )
    # Make parsable YAML
    header = pkg.campaign_header.read_text().format_map(asdict(metadata))
    fname_template_config = get_template_dir() / f"{metadata.template}.yaml"
    content = f"{header}\n{fname_template_config.read_text()}"
    fname_campaign_config.write_text(content)


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

    # Is the template available?
    if template not in available_templates():
        msg = f"Template {template} does not exist ..."
        log.warn(msg)
        raise ValueError(msg)

    # Does the campaign already exist?
    campaign_dir = _campaign_dir(name)
    if campaign_dir.is_dir():
        msg = f"Campaign directory {campaign_dir} exists ..."
        log.warn(msg)
        raise ValueError(msg)

    # Create

    # Create campaign directory
    log.info(f"Creating campaign directory {campaign_dir} ...")
    campaign_dir.mkdir(parents=True)

    add_campaign_to_bsw_menu(campaign_dir)
    build_campaign_directory_tree(campaign_dir)
    metadata = MetaData(
        username=getpass.getuser(),
        template=template,
        campaign=name,
        beg=beg.isoformat(),
        end=end.isoformat(),
    )
    create_campaign_configuration_file(campaign_dir, metadata)


def change_environment_variables(changes: list[dict[str, Any]]) -> None:
    for change in changes:
        variable = change.get("variable")
        # Anything can be given in the YAML document, but only a single-word
        # string is acceptable as variable name.
        if not (s := str(variable)) == variable or s.strip() != s or s.split()[0] != s:
            continue
        value = str(change.get("value"))
        os.environ[variable] = value


def load(name: str) -> dict[str, Any]:
    """
    Load a given campaign configuration.

    """
    ifname = _campaign_configuration(name)
    if not ifname.is_file():
        raise SystemExit(
            f"Campaign {name!r} does not exist or has no campaign-specific configuration file {ifname.name} ..."
        )
    c = configuration.with_env(ifname)
    if (changes := c.get("environment")) is not None:
        if isinstance(changes, list):
            change_environment_variables(changes)
    return c


def _campaign_subdirectories(name: str) -> dict[str, str]:
    """
    Get actual subdirectories directly beneath campaign directory.

    """
    root = _campaign_dir(name)
    return {p.name: p.path for p in os.scandir(root) if p.is_dir()}


def _delete_directory_content(path: str) -> None:
    """
    Remove all children in a given directory.

    """
    for child in Path(path).iterdir():
        print(f"Deleting {child!r}")
        if child.is_file() or child.is_symlink():
            child.unlink()
        if child.is_dir():
            shutil.rmtree(child)


def clean(name: str) -> None:
    """
    Clean specified paths inside campaign directory.

    """
    # Are there any directories specified?
    c = load(name)
    paths: list[str] | None = c.get("clean")
    if not paths:
        return

    dirs = _campaign_subdirectories(name)

    # Take those selected
    existing_chosen = [path for (name, path) in dirs.items() if name in paths]

    print("\n".join(existing_chosen))
    proceed = input("Proceed (y/[n]): ").lower() == "y"
    if not proceed:
        return

    # And delete their contents, but not the directories
    for path in existing_chosen:
        _delete_directory_content(path)
