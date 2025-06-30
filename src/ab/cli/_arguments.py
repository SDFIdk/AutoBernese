"""
Common command-line arguments

"""

import click

from ab.cli import _input


# Configuration
section = click.argument("section", default=None, type=str, required=False)

# Campaign
name = click.argument("name", type=str)
names = click.argument("names", nargs=-1, type=str)
template = click.argument("template", default=None, type=str, required=False)

# Date information
date = click.argument("date", type=_input.date)
week = click.argument("week", type=int)
year = click.argument("year", type=int)
doy = click.argument("doy", type=int)
