"""
Command-line interface for AutoBernese configuration content.

"""

import logging

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print

from ab import configuration
from ab.cli import (
    _arguments,
    _options,
)
from ab.bsw import campaign as _campaign


log = logging.getLogger(__name__)


@click.command
@_arguments.section
@_options.campaign
def config(section: str, campaign: str | None = None) -> None:
    """
    Show all or specified configuration section(s).

    """
    if campaign is not None:
        config = _campaign.load(campaign)
    else:
        config = configuration.load()

    if section is None:
        print(config)
    else:
        print(config.get(section, {}))
