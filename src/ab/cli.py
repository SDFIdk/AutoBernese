"""
Command-line interface

*   Prepare new station data
*   Download general data sources
*   Create campaign
*   Download input sources
*   Quality assurance
*   Preprocess input data for general use
*   Preprocess input data for campaign
*   Organise input data for the campaign
*   Run BPE for chosen campaign and PCF.
*   Set file ownership and permissions
*   Prepare end products
*   Quality control

"""
from typing import Any
import logging

import click
from rich import print

from ab import (
    bsw,
    configuration,
    data,
    organiser,
)

log = logging.getLogger(__name__)


@click.group
def main() -> None:
    ...


@main.command
def config(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Show configuration

    """
    print(configuration.load(*args, **kwargs))
    log.debug("Loaded config")


@main.command
def create_campaign(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Create campaign

    """
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
def run(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Run Bernese Processing Engine [BPE].

    """
    bsw.run(*args, **kwargs)


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
