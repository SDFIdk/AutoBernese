"""
Command-line interface

"""
import logging
from pathlib import Path
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
    pkg,
)
from ab.bsw import (
    campaign as _campaign,
    task as _task,
)
from ab.data import (
    source as _source,
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

    2.  Create Bernese campaigns using pre-defined campaign templates.

    3.  Download campaign-specific data.

    4.  Run the Bernese Processing Engine [BPE] for Bernese campaigns with an
        AutoBernese campaign configuration.

    """
    if show_version:
        print(f"{__version__}")
        raise SystemExit
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


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


# @main.command
# def bpe(campaign: str
#     pcf_file: str,
#     cpu_file: str,
#     year: str,
#     session: str,
#     sysout: str,
#     status: str,
#     taskid: str,
#     ) -> None:
#     """
#     Stand-alone tool for running the Bernese Processing Engine [BPE].

#     """
#     print("BPE")


@main.command
@click.option(
    "-f",
    "--force",
    help="Force the download of files that are already downloaded according to their maximum age.",
    required=False,
    is_flag=True,
)
@click.option(
    "-c",
    "--campaign",
    help="Download campaign-specific sources as defined in given campaign configuration.",
    required=False,
)
def download(force: bool = False, campaign: str | None = None) -> None:
    """
    Download all sources in the autobernese configuration file.

    """
    if campaign is not None:
        config = _campaign.load(campaign)
    else:
        config = configuration.load()

    source: _source.Source
    for source in config.get("sources", []):
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
    _campaign.init_template_dir()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@campaign.command
@click.option("--verbose", "-v", is_flag=True, help="Print more details.")
def ls(verbose: bool) -> None:
    """
    List existing campaigns

    """
    log.debug("List existing campaigns ...")
    print("Existing campaigns registered in the BSW campaign list:")
    print("\n".join(_campaign.ls(verbose)))


@campaign.command
@click.argument("template", default=None, type=str, required=False)
def templates(template: str | None) -> None:
    """
    List available campaign templates or show content of given template.

    """
    if template is None:
        log.debug("List available campaign templates ...")
        print("\n".join(_campaign.available_templates()))

    else:
        log.debug(f"Show raw template {template!r} ...")
        print(_campaign.load_template(template))


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
    _campaign.create(name, template, beg, end)


@campaign.command
@click.argument("name", type=str)
@click.option("--verbose", "-v", is_flag=True, help="Print more details.")
def sources(name: str, verbose: bool = False) -> None:
    """
    Print the campaign-specific sources.

    """
    sources: list[_source.Source] = _campaign.load(name).get("sources")
    formatted = (
        f"""\
{source.name=}
{source.url=}
{source.destination=}
"""
        for source in sources
    )

    if verbose:
        join = lambda pairs: "\n".join(f"{p.path_remote} -> {p.fname}" for p in pairs)
        formatted = (
            f"{info}{join(source.resolve())}\n"
            for (source, info) in zip(sources, formatted)
        )

    print("\n".join(sorted(formatted)))


@campaign.command
@click.argument("name", type=str)
def tasks(name: str) -> None:
    """
    Show tasks for a campaign.

    """
    task: _task.Task
    for task in _campaign.load(name).get("tasks"):
        print(task)
        print()


@campaign.command
@click.argument("name", type=str)
def runbpe(name: str) -> None:
    """
    Run the BPE for each tasks in the campaign configuration.

    """
    task: _task.Task
    for task in _campaign.load(name).get("tasks"):
        task.run()


@main.group()
def station() -> None:
    """
    Stand-alone tools for station data.

    """


@station.command
@click.argument("filename", type=Path)
def parse_sitelog(filename: Path) -> None:
    """
    Parse sitelog and print it to the screen.

    This command was created for debugging and may have some value as it can
    quickly show the fields that are extracted as part of creating a STA file
    from site-log files.

    Thus, not all fields from the site-log file are extracted.

    """
    print(json.dumps(sitelog.Sitelog(filename).sections_extracted, indent=2))


@station.command
@click.option(
    "-f",
    "--config",
    required=False,
    default=None,
    type=Path,
    help="Path to an input YAML file with the keys `sitelogs`, `individually_calibrated` and `output_sta_file` given.",
)
@click.option(
    "-i",
    "sitelogs",
    multiple=True,
    type=Path,
    help="One or more paths to site-log files to build the STA-file from.",
)
@click.option(
    "-c",
    "individually_calibrated",
    multiple=True,
    type=str,
    help="Four-letter ID for each station that is individually calibrated.",
)
@click.option(
    "-o",
    "output_filename",
    required=False,
    type=Path,
    default=Path(".").resolve() / "sitelogs.STA",
    help="Path to output filename for the STA file. If none given, the output is saved as ./sitelogs.STA.",
)
def sitelogs2sta(
    config: Path,
    sitelogs: tuple[Path],
    individually_calibrated: tuple[str],
    output_filename: Path,
) -> None:
    """
    Create a STA file from sitelogs.

    Choose one of the following ways to run it:

    1.  Supply at least one path to a sitelog and the sitelog will be created
        for it/these. -   With no ouput path given, create the STA file in the
        current working directory. -   Names of individually-calibrated stations
        can be given.

    2.  Supply the same possible options as in 1., but inside a YAML file. The
        file is loaded with the current Bernese environment, so advanced paths
        are possible.

    3.  Supply no arguments, and a STA file is created based on the input
        arguments given in the general or user-supplied configuration file.

    """
    if config is not None:
        log.info(f"Create STA file from arguments in given input-file.")
        # raise SystemExit
        kwargs = configuration.with_env(config)

    elif sitelogs:
        log.info(f"Create STA file from given arguments.")
        # raise SystemExit
        kwargs = dict(
            sitelogs=list(sitelogs),
            individually_calibrated=individually_calibrated,
            output_sta_file=output_filename,
        )

    elif configuration.load().get("station") is not None:
        log.info(f"Create STA file from arguments in the configuration.")
        # raise SystemExit
        kwargs = configuration.load().get("station")

    sta.create_sta_file_from_sitelogs(**kwargs)


@main.group()
def troposphere() -> None:
    """
    Stand-alone tools for troposphere data.

    """


@troposphere.command
# @click.argument("filename", type=Path)
def concat() -> None:  # filename: Path) -> None:
    """
    Concatenate hour files (`H%H`) with troposphere delay model into dayfiles.

    """
    from ab import vmf

    vmf.concat()


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
