"""
Module for working with campaigns in the current BSW environment.

"""
import datetime as dt
import getpass
from typing import (
    Any,
    Final,
)
from dataclasses import dataclass
from pathlib import Path
from string import Template
import shutil
import logging

import yaml

import ab
from ab import (
    pkg,
    configuration,
)
from ab.dates import date_range


log = logging.getLogger(__name__)

_CONF = configuration.load()

# Campaign-management configuration
_CAMPAIGN_CONF: Final[dict[str, Any]] = _CONF.get("campaign")
_CAMPAIGN_MENU: Final[Path] = _CAMPAIGN_CONF.get("menu")
_REQUIRED_CAMPAIGN_DIRECTORIES: Final[list[dict[str, Any]]] = _CAMPAIGN_CONF.get(
    "directories"
)
_TEMPLATE_DIR: Final[Path] = _CONF.get("runtime").get("campaign_templates")

# Current Bernese installation environment
_BSW_ENV: Final[dict[str, Any]] = configuration.load().get("bsw_env")

# Other
_P: Final[str] = "${P}"


def init_template_dir() -> dict[str, str]:
    """
    Create a directory for user-defined campaign templates in the autobernese
    directory.

    Does nothing if the template directory already exists.

    If it does not exist, the directory is created and the packaged default
    template is added.

    """
    if _TEMPLATE_DIR.is_dir():
        return

    log.info(f"Create campaign-template directory in {_TEMPLATE_DIR} ...")
    _TEMPLATE_DIR.mkdir(exist_ok=True, parents=True)

    log.info(
        f"Copy default template-campaign configuration {pkg.template_campaign} to {_TEMPLATE_DIR} ..."
    )
    shutil.copy(pkg.template_campaign, _TEMPLATE_DIR)


def available_templates() -> dict[str, str]:
    """
    Return list of available campaign templates.

    """
    return [fname.stem for fname in _TEMPLATE_DIR.glob("*.yaml")]


def load_template(template: Path | str) -> dict[str, Any]:
    if not template in available_templates():
        raise ValueError(f"Template {template!r} does not exist ...")
    ifname = (_TEMPLATE_DIR / template).with_suffix(".yaml")
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
    return [Template(s).safe_substitute(_BSW_ENV).strip('"') for s in lines]


def ls(verbose: bool = False) -> list[str]:
    """
    Return list of created campaigns.

    """
    raw = _extract_campaign_list(_CAMPAIGN_MENU.read_text())
    if not verbose:
        return raw

    dirs = [Path(r) for r in raw]
    lines = []
    # TODO: Remove the template string that is not needed.
    # fstr = "{directory} - {template} - {version} - {username} - {created}"
    fstr = "{directory} {template} {version} {username} {created}"
    default = dict(directory="", template="", version="", username="", created="")
    for d in dirs:
        kwargs = {**default, **dict(directory=d)}
        ifname = d / "campaign.yaml"
        if not ifname.is_file():
            lines.append(fstr.format(**kwargs))
            continue

        campaign = yaml.safe_load(ifname.read_text())
        meta = campaign.get("metadata")
        lines.append(fstr.format(**{**kwargs, **meta}))

    return lines


def _campaign_dir(name: str) -> Path:
    """
    Return the directory path to the campaign `name`.

    """
    return Path(_BSW_ENV.get("P")) / f"{name}"


def _campaign_configuration(name: str) -> Path:
    """
    Return the configuration-file path to the campaign `name`.

    """
    return _campaign_dir(name) / "campaign.yaml"


def build_campaign_menu(campaigns: list[str] = None) -> None:
    """
    Build content for a MENU_CMP.INP file with list of the given campaigns.

    If a campaign path matches that of the default Bernese campaign directory
    denoted `${P}`, the respective path component is replaced with these
    literals.

    """
    if not campaigns:
        log.info("No campaign list to format ...")
        return

    P = _BSW_ENV.get("P")
    formatted = [f'  "{campaign.replace(P, _P)}"' for campaign in campaigns]
    count = len(campaigns)
    separator = "\n" if count > 1 else ""
    campaigns = "\n".join(formatted)
    parameters = dict(count=count, separator=separator, campaigns=campaigns)
    return pkg.template_campaign_menu_list.read_text().format(**parameters)


def add_campaign_to_bsw_menu(path: str | Path) -> None:
    """
    Add given campaign path to the list of campaigns in the campaign-menu file
    in the Bernese installation directory.

    """
    path = Path(path)
    if not path.is_dir():
        raise ValueError(f"Path {path!r} is not a directory ...")

    # Load existing campaign-menu file
    raw = _CAMPAIGN_MENU.read_text()

    # Create a backup just as BSW does.
    _CAMPAIGN_MENU.with_suffix(".bck").write_text(raw)

    # Update the campaign list
    existing = set(_extract_campaign_list(raw))
    # Note: We convert the PosixPath to a string, and the make a single-element
    # set with that string before adding it to the existing list and sorting it.
    updated = sorted(existing | {f"{path}"})

    # Write the updated and formatted list to the campaign-menu file.
    _CAMPAIGN_MENU.write_text(build_campaign_menu(updated))


def create(name: str, template: str, beg: dt.date, end: dt.date) -> None:
    """
    Create a campaign.

    """
    log.info(f"Creating campaign with the following input:")
    log.info(f"{name=}")
    log.info(f"{template=}")
    log.info(f"{beg=}")
    log.info(f"{end=}")

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

    # Create campaign directory
    log.info(f"Creating campaign directory {campaign_dir} ...")
    campaign_dir.mkdir(parents=True)

    # Update the campaign-menu file in Bernese install directory
    add_campaign_to_bsw_menu(campaign_dir)

    # Create required campaign-directory tree
    log.info(f"Create required campaign-directory tree ...")
    for directory_info in _REQUIRED_CAMPAIGN_DIRECTORIES:
        # We are creating a new directory in an existing one
        path_full = campaign_dir / directory_info.get("name")
        path_full.mkdir()

        # Any specified file paths are copied over to the new directory
        for fname_source in directory_info.get("files", []):
            shutil.copy(fname_source, path_full / Path(fname_source).name)

    # Create AutoBernese campaign-configuration file
    fname_campaign_config = campaign_dir / "campaign.yaml"
    log.info(
        f"Creating AutoBernese campaign-configuration file {fname_campaign_config} ..."
    )
    # Make parsable YAML
    header_data = dict(
        version=ab.__version__,
        created=dt.datetime.now().isoformat()[:19],
        username=getpass.getuser(),
        template=template,
        beg=beg.isoformat(),
        end=end.isoformat(),
    )
    header = pkg.campaign_header.read_text().format(**header_data)
    fname_template_config = _TEMPLATE_DIR / f"{template}.yaml"
    content = f"{header}\n{fname_template_config.read_text()}"
    fname_campaign_config.write_text(content)


def load(name: str) -> dict[str, Any]:
    """
    Load a given campaign configuration.

    """
    ifname = _campaign_configuration(name)
    if not ifname.is_file():
        raise RuntimeError(
            f"Campaign {name} has no campaign-specific configuration file {ifname.name} ..."
        )
    return configuration.with_env(ifname, keep_env=False)
