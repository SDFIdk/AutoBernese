"""
Command-line interface

"""
import logging
import pathlib
import json
import datetime as dt
from typing import (
    Any,
    Final,
)

import click
from rich import print

from ab import (
    __version__,
    configuration,
    dates,
    bsw,
    organiser,
)
from ab.data import (
    ftp,
    http,
)
from ab.station import (
    sitelog,
    sta,
)


log = logging.getLogger(__name__)


DATE_FORMAT: Final[str] = "%Y-%m-%d"


def date(s: str) -> dt.date:
    return dt.datetime.strptime(s, DATE_FORMAT).date()


@click.group(invoke_without_command=True)
@click.option("--version", "show_version", is_flag=True, default=False)
@click.pass_context
def main(ctx: click.Context, show_version: bool) -> None:
    """
    AutoBernese is a Danish army knife that

    1.  Downloads external data to your local data storage.

    2.  Creates and manages Bernese campaigns.

    3.  Runs Bernese Processing Engine [BPE] for campaigns created with
        AutoBernese.

    """
    if show_version:
        print(f"{__version__}")
        raise SystemExit
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command
def env() -> None:
    """
    Show BSW environment loaded into autobernese configuration

    """
    print(configuration.load().get("bsw_env"))


@main.command
@click.argument("section", default=None, type=str)
def config(section: str) -> None:
    """
    Show specified configuration section or all if no section name given.

    """
    c = configuration.load()
    if section is None:
        print(c)
    else:
        print(c.get(section, {}))


@main.command
def logfile() -> None:
    """
    Follow log file (run `tail -f path/to/logfile.log`).

    """
    filename = configuration.load().get("environment").get("logging").get("filename")
    import subprocess as sub

    try:
        log.debug(f"Show log tail ...")
        process = sub.Popen(["/usr/bin/tail", "-f", f"{filename}"])
        process.wait()

    except KeyboardInterrupt:
        log.debug(f"Log tail finished ...")

    finally:
        process.terminate()
        process.kill()


@main.group
def dateinfo() -> None:
    """
    Date information

    """


@dateinfo.command
@click.argument("date", type=date)
def ymd(date: dt.date) -> None:
    """
    Show date information based on date.

    """
    gps_date = dates.GPSDate.from_date(date)
    print(json.dumps(gps_date.dateinfo(), indent=2))


@dateinfo.command
@click.argument("week", type=int)
def gpsweek(week: int) -> None:
    """
    Show date information based on GPS week.

    """
    gps_date = dates.GPSDate.from_gps_week(week)
    print(json.dumps(gps_date.dateinfo(), indent=2))


@dateinfo.command
@click.argument("year", type=int)
@click.argument("doy", type=int)
def ydoy(year: int, doy: int) -> None:
    """
    Show date information based on Year and day of year [DOY].

    """
    gps_date = dates.GPSDate.from_year_doy(year, doy)
    print(json.dumps(gps_date.dateinfo(), indent=2))


@main.command
@click.option(
    "-f",
    "--force",
    help="Download files that are already downloaded according to their maximum age.",
    required=False,
    is_flag=True,
)
def download_sources(force: bool = False) -> None:
    """
    Download sources based on souece specification in the configuration file.

    So far a source entry is assumed to be a Source instance.

    """
    sources = configuration.load().get("data").get("sources")
    for source in sources:
        msg = f"Download source: {source.name}"
        print(msg)
        log.debug(msg)

        if force:
            source.max_age = 0

        match source.protocol:
            case "ftp":
                ftp.download(source)
            case "http" | "https":
                http.download(source)
    else:
        msg = "Finished downloading sources"
        print(msg)
        log.debug(msg)


@main.group(invoke_without_command=True)
@click.pass_context
def campaign(ctx: click.Context) -> None:
    """
    Campaign-specific actions.

    """
    bsw.campaign.init_template_dir()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@campaign.command
@click.option("--verbose", "-v", is_flag=True, help="Print details.")
def ls(verbose: bool) -> None:
    """
    List existing campaigns

    """
    log.debug("List existing campaigns ...")
    print("Existing campaigns registered in the BSW campaign list:")
    print("\n".join(bsw.campaign.ls(verbose)))


@campaign.command
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help=f"The name of the campaign.",
)
def sources(name: str) -> None:
    """
    Print campaign-specific sources.

    """
    sources = bsw.campaign.load(name).get("sources")
    print("\n".join(f"{s.name} - {s.url}" for s in sources))


@campaign.command
def templates() -> None:
    """
    List available campaign templates

    """
    # TODO: make separate of renamed command that shows list of existing templates or shows the content of template with given name.
    log.debug("List available campaign templates ...")
    print("\n".join(bsw.campaign.available_templates()))


@campaign.command
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help=f"The name of the campaign.",
)
@click.option(
    "-t",
    "--template",
    type=str,
    default="default",
    required=False,
    help="Template for campaign configuration If not given, the default configuration is used.",
)
@click.option(
    "-b",
    "--beg",
    type=date,
    required=True,
    help=f"Format: {DATE_FORMAT}",
)
@click.option(
    "-e",
    "--end",
    type=date,
    required=True,
    help=f"Format: {DATE_FORMAT}",
)
def create(name: str, template: str, beg: dt.date, end: dt.date) -> None:
    """
    Create a campaign directory based on the specified template and adds the
    campaign path to the list of available campaigns in the corresponding menu.

    """
    log.debug(f"Create campaign {name=} using {template=} with {beg=} and {end=} ...")
    bsw.campaign.create(name, template, beg, end)


@campaign.command
# @click.argument(
#     "campaign",
#     type=str,
#     help="Campaign",
# )
def recipes(campaign: str) -> None:
    """
    Show the recipes for the active campaign.

    """
    # active = state.active_campaign()
    for recipe in bpe.get_recipes():
        print(recipe)


@main.group(invoke_without_command=True)
@click.pass_context
def bpe(ctx) -> None:
    """
    Tools for the Bernese Processing Engine [BPE].

    """
    print("BPE")


@bpe.command
def run(**bpe_settings: dict[Any, Any]) -> None:
    """
    Run Bernese Processing Engine [BPE].

    """
    # bsw.runbpe(bpe_settings)
    bsw.runbpe()


@main.command
@click.argument("filename", type=pathlib.Path)
def parse_sitelog(filename: pathlib.Path) -> None:
    """
    Parse sitelog and print it to the screen

    """
    print(json.dumps(sitelog.Sitelog(filename).sections_extracted, indent=2))


@main.command
# @click.argument("sitelog_filenames", type=list[pathlib.Path])
# @click.argument("individually_calibrated", type=list[str])
# @click.argument("filename", type=pathlib.Path)
def sitelogs2sta(
    # sitelog_filenames: list[pathlib.Path],
    # individually_calibrated: list[str],
    # filename: pathlib.Path,
) -> None:
    """
    Create STA file from sitelogs

    """
    sta.create_sta_file_from_sitelogs(**configuration.load().get("station"))


# @main.command
# def prepare_campaign_data(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
#     """
#     Organises campaign data

#     """
#     organiser.prepare_campaign_data(*args, **kwargs)


# @main.command
# def prepare_end_products(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
#     """
#     Organises campaign end products.

#     """
#     organiser.prepare_end_products(*args, **kwargs)


# @main.command
# def submit_end_products(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
#     """
#     Submits campaign end products.

#     """
#     organiser.submit_end_products(*args, **kwargs)
