"""
Command-line interface for AutoBernese

"""

import logging
import json
import datetime as dt
from dataclasses import (
    asdict,
)

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print

from ab import (
    __version__,
    configuration,
)
from ab.bsw import (
    get_bsw_release,
)

from ab.cli import (
    _input,
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

    3.  Run the BPE for campaigns with an AutoBernese configuration.

    4.  Do various other things related to GNSS-data processing.

    """
    if show_version:
        print(f"{__version__}")
        raise SystemExit

    if not configuration.LOADGPS_setvar_sourced():
        msg = "Not all variables in LOADGPS.setvar are set ..."
        print(f"[white on red]{msg}[/]")
        raise SystemExit

    configuration.set_up_runtime_environment()

    if bsw_release:
        print(json.dumps(asdict(get_bsw_release()), indent=2))
        raise SystemExit

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        raise SystemExit


main.add_command(config.config)
main.add_command(logs.logs)
main.add_command(qc.qc)
main.add_command(dateinfo.dateinfo, aliases=["dt"])
main.add_command(download.download, aliases=["dl"])
main.add_command(campaign.campaign, aliases=["c"])
main.add_command(station.station, aliases=["st"])
main.add_command(troposphere.troposphere, aliases=["tr"])
