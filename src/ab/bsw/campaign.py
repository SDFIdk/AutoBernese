"""
Module for working with campaigns in the current BSW environment.

"""
import datetime as dt
import getpass
from typing import Any
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


def _campaign_config() -> dict[str, Any]:
    return configuration.load().get("campaign")


def _template_dir() -> Path:
    return _campaign_config().get("templates")


def _required_campaign_directories() -> list[dict[str, Any]]:
    return _campaign_config().get("directories")


def init_template_dir() -> dict[str, str]:
    """
    Check if campaign-template directory exists.

    Create a new one with campaign type `default` adding the latest version of
    the package.

    """
    template_dir = _template_dir()
    template = template_dir / pkg.campaign_template.name

    if template.is_file():
        return

    if not template_dir.is_dir():
        log.info(f"Creating campaign-template directory in {template_dir} ...")
        template_dir.mkdir(exist_ok=True, parents=True)

    log.info(f"Copy campaign-template {pkg.campaign_template} to {template_dir} ...")
    shutil.copy(pkg.campaign_template, template_dir)


def available_templates() -> dict[str, str]:
    """
    Return list of available campaign templates.

    """
    template_dir = _template_dir()
    return [fname.stem for fname in template_dir.glob("*.yaml")]


def _extract_campaign_list(raw: str) -> list[str]:
    meat = raw.split("  ## widget")[0]
    meat = meat.split("CAMPAIGN ")[1]
    meat = meat.split(maxsplit=1)[1].strip()
    lines = [item.strip() for item in meat.splitlines()]
    bsw_env = configuration.load().get("bsw_env")
    return [Template(s).safe_substitute(bsw_env) for s in lines]


def ls() -> list[str]:
    """
    Return list of created campaigns.

    """
    return _extract_campaign_list(_campaign_config().get("menu").read_text())


def _bsw_env(key: str) -> str:
    return configuration.load().get("bsw_env").get(key)


def _campaign_dir(name: str) -> Path:
    return Path(_bsw_env("P")) / f"{name}"


# def _campaign_dir(template: str) -> Path:
#     P = configuration.load().get('bsw_env').get('P')
#     return Path(P).joinpath(template) / f"{template}{week}"


# def _campaign_file(week: int | str, template: str) -> Path:
#     return _campaign_dir(template) / f"{template}{week}"


def load(name: str) -> dict[str, Any]:
    ifname = _campaign_dir(name) / "campaign.yaml"
    return yaml.safe_load(ifname.read_text())


_P = "${P}"


def menu():
    from rich import print

    P = configuration.load().get("bsw_env").get("P")

    campaigns = [
        "${P}/EXAMPLE",
        "/path/to/CAMPAIGN54/foo2222",
        "/some/other/path/tmp/foo",
    ]
    formatted = [f'  "{campaign.replace(P, _P)}"' for campaign in campaigns]
    count = len(campaigns)
    separator = "\n" if count > 1 else ""
    campaigns = "\n".join(formatted)

    parameters = dict(
        count=count,
        separator=separator,
        campaigns=campaigns,
    )

    print(pkg.campaign_list_template.read_text().format(**parameters))


def sources(name: str) -> None:
    from rich import print

    print(c := load(name))
    from IPython import embed

    embed()
    raise SystemExit


# def create(gps_week: GPSWeek, template: str) -> None:
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
    campaign_dir = Path(_bsw_env("P")) / f"{name}"
    if campaign_dir.is_dir():
        msg = f"Campaign directory {campaign_dir} exists ..."
        log.warn(msg)
        raise ValueError(msg)

    # Create campaign directory
    log.info(f"Creating campaign directory {campaign_dir} ...")
    campaign_dir.mkdir(parents=True)

    # Create required campaign-directory tree
    log.info(f"Create required campaign-directory tree ...")
    for directory_info in _required_campaign_directories():
        path_full = campaign_dir / directory_info.get("name")
        path_full.mkdir()
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
        beg=beg.isoformat(),
        end=end.isoformat(),
    )
    header = pkg.campaign_header.read_text().format(**header_data)
    fname_template_config = _template_dir() / f"{template}.yaml"
    content = f"{header}\n{fname_template_config.read_text()}"
    fname_campaign_config.write_text(content)


# @dataclass
# class Campaign:
#     beg: dt.date
#     end: dt.date

#     @property
#     def gpsweeks(self) -> list[GPSWeek]:
#         return list(set(doy(d) for d in date_range(self.beg, self.end)))