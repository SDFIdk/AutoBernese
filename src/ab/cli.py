"""
Command-line interface

"""
import logging
import pathlib
import json
from typing import Any

import click
from rich import print

from ab import (
    configuration,
    data,
    bsw,
    organiser,
    sitelog,
    sta,
)


log = logging.getLogger(__name__)


@click.group
def main() -> None:
    """
    Root command group for subsequent groups and actions.

    """


@main.command
def config(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Show configuration

    """
    print(configuration.load(*args, **kwargs))
    log.debug("Configuration loaded ...")


@main.command
@click.argument("filename", type=pathlib.Path)
def parse_sitelog(filename: pathlib.Path) -> None:
    """
    Parse sitelog and print it to the screen

    """
    print(json.dumps(sitelog.Sitelog(filename).sections_extracted, indent=2))


@main.command
@click.argument("sitelog_filenames", type=list[pathlib.Path])
@click.argument("individually_calibrated", type=list[str])
@click.argument("filename", type=pathlib.Path)
def create_sta_file_from_sitelogs(
    sitelog_filenames: list[pathlib.Path],
    individually_calibrated: list[str],
    filename: pathlib.Path,
) -> None:
    """
    Create STA file from sitelogs

    """
    # sta.create_sta_file_from_sitelogs(sitelog_filenames, individually_calibrated, filename)
    sta.main()


@main.group
def campaign() -> None:
    """
    Command group for campaign-specific actions.

    """


@campaign.command
def create(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Create campaign

    """
    log.debug("Create campaign ...")
    bsw.create_campaign(*args, **kwargs)


@main.command
def download_sources(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Download sources based on campaign configuration file.

    """
    data.download_sources(*args, **kwargs)


@main.command
def prepare_campaign_data(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Organises campaign data

    """
    organiser.prepare_campaign_data(*args, **kwargs)


@main.command
def bpe(**bpe_settings: dict[Any, Any]) -> None:
    """
    Run Bernese Processing Engine [BPE].

    """
    bsw.runbpe(bpe_settings)


@main.command
def prepare_end_products(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Organises campaign end products.

    """
    organiser.prepare_end_products(*args, **kwargs)


@main.command
def submit_end_products(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Submits campaign end products.

    """
    organiser.submit_end_products(*args, **kwargs)
