"""
Command-line interface for AutoBernese

"""

import logging

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print

from ab import configuration
from ab.cli import (
    _input,
    about,
    config,
    logs,
    qc,
    dateinfo,
    campaign,
    station,
    troposphere,
    download,
)


log = logging.getLogger(__name__)


@click.group(cls=ClickAliasedGroup, invoke_without_command=True)
@click.option("--version", "show_version", is_flag=True, default=False)
@click.option("--bsw-release", "bsw_release", is_flag=True, default=False)
@click.pass_context
def main(ctx: click.Context, show_version: bool, bsw_release: bool) -> None:
    """
    AutoBernese is a tool that can

    1.  Create Bernese campaigns using its built-in template system.

    2.  Download and organise data for general or campaign-specific use.

    3.  Run campaign-specific tasks like the Bernese Processing Engine.

    4.  Do other things related to Bernese and GNSS-data processing.

    """

    if show_version:
        print(about.autobernese())
        raise SystemExit

    if bsw_release:
        print(about.bernese())
        raise SystemExit

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        raise SystemExit

    configuration.set_up_runtime_environment()


main.add_command(config.config)
main.add_command(logs.logs)
main.add_command(qc.qc)
main.add_command(dateinfo.dateinfo, aliases=["dt"])
main.add_command(download.download, aliases=["dl"])
main.add_command(campaign.campaign, aliases=["c"])
main.add_command(station.station, aliases=["st"])
main.add_command(troposphere.troposphere, aliases=["tr"])
