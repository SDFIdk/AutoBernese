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
    vmf,
)
from ab.bsw import (
    campaign as _campaign,
    task as _task,
)
from ab.data import (
    DownloadStatus,
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

    sources = config.get("sources", [])

    s = 's' if len(sources) else ''
    msg = f"Resolving {len(sources)} source{s} ..."
    log.info(msg)

    source: _source.Source
    status_total = DownloadStatus()
    for source in sources:

        msg = f"Source: {source.name}"
        print(msg)
        log.debug(msg)

        if force:
            source.max_age = 0

        match source.protocol:
            case "ftp":
                status = ftp.download(source)
                status_total += status
            case "http" | "https":
                status = http.download(source)
                status_total += status
        print(f"  Downloaded: {status.downloaded}\n  Existing: {status.existing}")
    else:
        msg = "Finished downloading sources ..."
        print(msg)
        log.debug(msg)
        print(f"Overall status:")
        print(f"  Downloaded: {status_total.downloaded}\n  Existing: {status_total.existing}")


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
    msg = f"Create campaign {name=} using {template=} with {beg=} and {end=} ..."
    print(msg)
    log.info(msg)
    _campaign.create(name, template, beg, end)


@campaign.command
@click.argument("name", type=str)
@click.option("--verbose", "-v", is_flag=True, help="Print more details.")
def sources(name: str, verbose: bool = False) -> None:
    """
    Print the campaign-specific sources.

    """
    sources: list[_source.Source] | None = _campaign.load(name).get("sources")

    if sources is None:
        msg = f"No sources found"
        print(msg)
        log.info(msg)
        return

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
    tasks: list[_task.Task] | None = _campaign.load(name).get("tasks")

    if tasks is None:
        msg = f"No tasks found"
        print(msg)
        log.info(msg)
        return

    for task in tasks:
        print(task)
        print()


@campaign.command
@click.argument("name", type=str)
def run(name: str) -> None:
    """
    Resolve campaign tasks and run them all.

    """
    tasks: list[_task.Task] | None = _campaign.load(name).get("tasks")

    if tasks is None:
        msg = f"No tasks found"
        print(msg)
        log.info(msg)
        return

    for task in tasks:
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
    Create a STA file from sitelogs and other station info.

    -   Site-log filenames are required.
    -   Four-letter IDs for individually-calibrated stations are optional.
    -   The path to the output STA file is optional. (If none given, the file
        will be written to sitelogs.STA in the current working directory.)

    Choose one of the following ways to run it:

    1.  Supply needed and optional arguments on the command line.

    2.  Supply path to a YAML file with the needed and/or optional arguments.

        The file is loaded with the current Bernese environment, so advanced
        paths are possible, e.g. `!Path [*D, station, sitelogs.STA]`.

    3.  Supply no arguments, and a STA file is created based on the input
        arguments given in the general or user-supplied configuration file.

    """
    kwargs: dict[str, Any] | None = None
    if config is not None:
        log.info(f"Create STA file from arguments in given input-file.")
        kwargs = configuration.with_env(config)

    elif sitelogs:
        log.info(f"Create STA file from given arguments.")
        kwargs = dict(
            sitelogs=list(sitelogs),
            individually_calibrated=individually_calibrated,
            output_sta_file=output_filename,
        )

    elif configuration.load().get("station") is not None:
        log.info(f"Create STA file from arguments in the configuration.")
        kwargs = configuration.load().get("station")

    if kwargs is None:
        msg = f"No tasks found"
        print(msg)
        log.info(msg)
        return
    sta.create_sta_file_from_sitelogs(**kwargs)


@main.group()
def troposphere() -> None:
    """
    Stand-alone tools for troposphere data.

    """


@troposphere.command
@click.argument("ipath", type=str)
@click.argument("opath", type=str)
@click.option(
    "-b",
    "--beg",
    type=date,
    help=f"Format: {DATE_FORMAT}",
)
@click.option(
    "-e",
    "--end",
    type=date,
    help=f"Format: {DATE_FORMAT}",
)
def status(ipath: str, opath: str, beg: dt.date | None, end: dt.date | None) -> None:
    """
    Show status for all possible VMF3 dates.

    """
    print(vmf.status(ipath, opath, beg, end))


@troposphere.command
@click.argument("ipath", type=str)
@click.argument("opath", type=str)
@click.option(
    "-b",
    "--beg",
    type=date,
    help=f"Format: {DATE_FORMAT}",
)
@click.option(
    "-e",
    "--end",
    type=date,
    help=f"Format: {DATE_FORMAT}",
)
def build(ipath: str, opath: str, beg: dt.date | None, end: dt.date | None) -> None:
    """
    Concatenate hour files (`H%H`) with troposphere delay model into dayfiles.

    """
    vmf.build(ipath, opath)
