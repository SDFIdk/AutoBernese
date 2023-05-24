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
    pkg,
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
    AutoBernese is a tool that can

    1.  Download external data to your local data storage.

    2.  Create and manage Bernese campaigns.

    3.  Run Bernese Processing Engine [BPE] for campaigns created with
        AutoBernese.

    """
    if show_version:
        print(f"{__version__}")
        raise SystemExit
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command
@click.argument("filename", type=str)
def test(filename: str) -> None:
    """
    Test feature.

    """
    print(configuration.with_env(filename))


@main.command
@click.argument("section", default=None, type=str, required=False)
def config(section: str) -> None:
    """
    Show all or specified configuration section(s).

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
    runtime = configuration.load().get("runtime")
    filename = runtime.get("logging").get("filename")
    import subprocess as sub

    try:
        log.debug(f"Show log tail ...")
        process = sub.Popen(["/usr/bin/tail", "-f", f"{filename}"])
        process.wait()

    except KeyboardInterrupt:
        log.debug(f"Log tail finished ...")
        print()

    finally:
        process.terminate()
        process.kill()


@main.group
def dateinfo() -> None:
    """
    Print date info on date, year+doy or GPS week.

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
def bpe(**bpe_settings: dict[Any, Any]) -> None:
    """
    Stand-alone tool for running the Bernese Processing Engine [BPE].

    """
    print("BPE")


@main.command
@click.option(
    "-f",
    "--force",
    help="Force the download of files that are already downloaded according to their maximum age.",
    required=False,
    is_flag=True,
)
def download_sources(force: bool = False) -> None:
    """
    Download all sources in the autobernese configuration file.

    """
    sources = configuration.load().get("sources")
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
    Create campaigns and manage campaign-specific sources and run BPE tasks.

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
@click.argument("template", default=None, type=str, required=False)
def templates(template: str | None) -> None:
    """
    List available campaign templates

    """
    if template is None:
        log.debug("List available campaign templates ...")
        print("\n".join(bsw.campaign.available_templates()))

    else:
        log.debug(f"Show raw template {template!r} ...")
        print(bsw.campaign.load_template(template))


@campaign.command
@click.argument("name", type=str)
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
    Create a Bernese campaign with directory content based on the specified
    template and add campaign path to the list of available campaigns in the BSW
    campaign menu.

    """
    log.debug(f"Create campaign {name=} using {template=} with {beg=} and {end=} ...")
    bsw.campaign.create(name, template, beg, end)


@campaign.command
@click.argument("name", type=str)
def sources(name: str) -> None:
    """
    Print the campaign-specific sources.

    """
    sources = bsw.campaign.load(name).get("sources")
    print("\n".join(f"{s.name} - {s.url}" for s in sources))


@campaign.command
@click.argument("name", type=str)
def tasks(name: str) -> None:
    """
    Show BPE tasks for a campaign.

    """
    for task in bsw.campaign.load(name).get("tasks"):
        print(task)
        print()


@campaign.command
@click.argument("name", type=str)
def runbpe(name: str) -> None:
    """
    Run the BPE for each tasks in the campaign configuration.

    """
    # c = campaigns...
    # for task in c.bpe_tasks:
    #     bsw.runbpe(bpe_settings)


@main.group()
def station() -> None:
    """
    Stand-alone tools for station data.

    """


@station.command
@click.argument("filename", type=pathlib.Path)
def parse_sitelog(filename: pathlib.Path) -> None:
    """
    Parse sitelog and print it to the screen

    """
    print(json.dumps(sitelog.Sitelog(filename).sections_extracted, indent=2))


@station.command
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
