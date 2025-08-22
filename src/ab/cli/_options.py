"""
Common command-line options

"""

import typing as t

import click
from click.core import (
    Context,
    Option,
    Argument,
)

from ab.cli import _input


FORMAT: t.Final = f"Format: {_input.DATE_FORMAT}"
"Date-format help string"


def set_yes(ctx: Context, param: Argument | Option, value: bool) -> None:
    if value is True:
        _input.set_prompt_proceed_yes()


# Command input
yes = click.option(
    "--yes", "-y", is_flag=True, help="Continue without asking.", callback=set_yes
)

# Command output
verbose = click.option("--verbose", "-v", is_flag=True, help="Print more details.")

# Command attitude
force = click.option(
    "-f", "--force", help="Force action.", required=False, is_flag=True
)

# General input
ipath = click.option("-i", "--ipath", type=str)
opath = click.option("-o", "--opath", type=str)
beg = click.option("-b", "--beg", type=_input.date, help=f"Start date. {FORMAT}")
end = click.option("-e", "--end", type=_input.date, help=f"End date. {FORMAT}")

# Campaign
campaign = click.option(
    "-c",
    "--campaign",
    "name",
    help="Use specified campaign configuration.",
    required=False,
)
template = click.option(
    "-t",
    "--template",
    type=str,
    default="default",
    required=False,
    help="Template for campaign configuration If not given, the default configuration is used.",
)
gps_week = click.option(
    "-g", "--gps-week", type=int, required=False, help=f"GPS-week number"
)

# Tasks and sources
identifiers = click.option(
    "-i",
    "--identifier",
    "identifiers",
    multiple=True,
    type=str,
    default=[],
    required=False,
    help="Use item with selected identifier. Exclude others not mentioned.",
)
exclude = click.option(
    "-x",
    "--exclude",
    multiple=True,
    type=str,
    default=[],
    required=False,
    help="Exclude item with selected identifier. Include others not mentioned.",
)

# Troposphere
hour_file_format = click.option("-h", "--hour-file-format", "ifname", type=str)
day_file_format = click.option("-d", "--day-file-format", "ofname", type=str)
