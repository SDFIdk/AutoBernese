"""
Module for working with campaigns in the current BSW environment.

"""
from typing import Any
from pathlib import Path
import shutil
import logging

import ab
from ab import (
    pkg,
    configuration,
)
from ab.gps import GPSWeek


log = logging.getLogger(__name__)


def _template_dir() -> Path:
    config = configuration.load().get("campaign")
    return config.get("templates")


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
    template_dir = configuration.load().get("campaign").get("templates")
    return [fname.stem for fname in template_dir.glob("*.yaml")]


def ls() -> None:
    """
    Return list of campaigns.

    TODO: Return a list of cleaned names?

    """
    config = configuration.load().get("campaign")
    content = config.get("menu").read_text()
    meat = content.split("  ## widget")[0]
    meat = meat.split("CAMPAIGN ")[1]
    meat = meat.split(maxsplit=1)[1].strip()
    return [item.strip() for item in meat.splitlines()]


# def _campaign_dir(template: str) -> Path:
#     P = configuration.load().get('bsw_env').get('P')
#     return Path(P).joinpath(template) / f"{template}{week}"


# def _campaign_file(week: int | str, template: str) -> Path:
#     return _campaign_dir(template) / f"{template}{week}"


def create(gps_week: GPSWeek, template: str) -> None:
    """
    Create a campaign.

    """
    # config = configuration.load().get("campaign")
    # menu = config.get("menu")
    # log.debug(f"{str(menu)} exists? {menu.is_file()} ...")

    from rich import print

    # print(menu.read_text())

    print(gps_week.date())

    if template not in available_templates():
        msg = f"Template {template} does not exist ..."
        log.warn(msg)
        raise ValueError(msg)

    P = configuration.load().get("bsw_env").get("P")
    campaign_dir = Path(P).joinpath(template) / f"{template}{gps_week.week}"

    if campaign_dir.is_dir():
        msg = f"Campaign directory {campaign_dir} exists ..."
        log.warn(msg)
        raise ValueError(msg)

    log.info(f"Creating campaign directory {campaign_dir} ...")
    campaign_dir.mkdir(parents=True)

    # File to be
    campaign_conf = campaign_dir / "campaign.yaml"

    # Template to copy
    template_conf = _template_dir() / f"{template}.yaml"

    log.info(f"Copying template {template_conf} to {campaign_dir} ...")
    shutil.copy(template_conf, campaign_conf)

    # Format the file content to make it parsable YAML
    parameters = dict(
        version=ab.__version__,
        gpsweek=gps_week.week,
    )
    header = pkg.campaign_header.read_text().format(**parameters)
    replaced = f"{header}\n{campaign_conf.read_text()}"
    campaign_conf.write_text(replaced)
