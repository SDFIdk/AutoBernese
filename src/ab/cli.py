"""
Command-line interface

"""
from typing import Any
import logging

import click
from rich import print

from ab import (
    configuration,
    data,
    bsw,
    organiser,
)
from ab.preprocessing import (
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
def read_sitelog(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Parse sitelog

    """
    print("This is a temporary command")
    sitelog.main()


@main.command
def create_sta_file(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Create STA file

    """
    print("This is a temporary command")
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
def runbpe(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Run Bernese Processing Engine [BPE].

    """
    # bsw.runbpe(*args, **kwargs)
    bsw.runbpe()


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
