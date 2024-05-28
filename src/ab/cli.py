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
from dataclasses import asdict

import click
from click_aliases import ClickAliasedGroup
from rich import print
import humanize

from ab import (
    __version__,
    configuration,
    dates,
    vmf,
)
from ab.bsw import (
    get_bsw_release,
    campaign as _campaign,
    task as _task,
)
from ab.qaqc import (
    check_example,
)
from ab.data import (
    DownloadStatus,
    source as _source,
    ftp,
    http,
    file,
)
from ab.station import (
    sitelog,
    sta,
)


log = logging.getLogger(__name__)


DATE_FORMAT: Final = "%Y-%m-%d"


def date(s: str) -> dt.date:
    return dt.datetime.strptime(s, DATE_FORMAT).date()


def print_versions() -> None:
    print(f"AutoBernese version {__version__}; BSW version {get_bsw_release()}")


@click.group(cls=ClickAliasedGroup, invoke_without_command=True)
@click.option("--version", "show_version", is_flag=True, default=False)
@click.option("--bsw-release", "bsw_release", is_flag=True, default=False)
@click.pass_context
def main(ctx: click.Context, show_version: bool, bsw_release: bool) -> None:
    """
    AutoBernese is a tool that can

    1.  Create Bernese campaigns using the built-in template system.

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


# @main.command
# def aliases() -> None:
#     """
#     Show YAML anchors in AutoBernese configuration and count the number of times
#     each one is alias in the environment.

#     """
#     from ab import pkg
#     import yaml
#     import collections as cs

#     parsed = yaml.parse(pkg.env.read_text())
#     # composed = yaml.compose(pkg.env.read_text())
#     events = list(parsed)
#     anchors = {
#         event.anchor
#         for event in events
#         if getattr(event, "anchor", None) is not None
#         and not isinstance(event, yaml.AliasEvent)
#     }
#     counter = cs.Counter({anchor: 0 for anchor in anchors})
#     aliased = [event.anchor for event in events if isinstance(event, yaml.AliasEvent)]
#     counter.update(aliased)
#     print(counter.most_common(10))

#     # from IPython import embed; embed(); raise SystemExit


@main.command
@click.argument("section", default=None, type=str, required=False)
@click.option(
    "-c",
    "--campaign",
    help="See specific campaign configuration.",
    required=False,
)
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


@main.command
def logs() -> None:
    """
    Follow log file (run `tail -f path/to/logfile.log`).

    """
    runtime = configuration.load().get("runtime")
    filename = runtime.get("logging").get("filename")
    import subprocess as sub

    process: sub.Popen | None = None
    try:
        log.debug(f"Show log tail ...")
        process = sub.Popen(["/usr/bin/tail", "-f", f"{filename}"])
        process.wait()

    except KeyboardInterrupt:
        log.debug(f"Log tail finished ...")

    finally:
        print()
        if process is not None:
            process.terminate()
            process.kill()


@main.group
def qc() -> None:
    """
    Quality-control measures

    """


@qc.command
@click.option("-s", "substitute", is_flag=True, default=False)
@click.option(
    "-r",
    "replacement",
    help="Replace zeros with given character.",
    required=False,
    default="·",
)
@click.option(
    "-t",
    "tolerance",
    help="Minimally-accepted tolerance for any residual in metres.",
    required=False,
    default=0.0001,
)
@click.option("-w", "show_weighted", is_flag=True, default=False)
def residuals(
    substitute: bool, replacement: str, tolerance: float, show_weighted: bool
) -> None:
    """
    Check the installation integrity for Bernese GNSS Software by comparing
    available results from running the EXAMPlE campaign against the reference
    files.

    For our purposes, we only need to check the residuals (reference minus
    result) of the coordinates for the stations that had their coordinates
    calculated.

    Assumptions include:

    *   The stations available in the reference result files are in the same
        order and include the same stations that are available in the results we
        produce ourselves.

    """
    # Make sure we only use a single character
    replacement = replacement[0]

    pairs = check_example.get_available_comparables()
    for pair in pairs:
        fname_reference = pair.get("reference")
        fname_result = pair.get("result")

        reference = check_example.extract_coordinates(fname_reference.read_text())
        result = check_example.extract_coordinates(fname_result.read_text())

        diff = reference - result

        print(f"Reference ({reference.date}): {fname_reference.name}")
        print(f"Result    ({result.date}): {fname_result.name}")
        sz = 8
        header = f"{'ID': <4s} {'Delta x': >{sz}s}  {'Delta y': >{sz}s}  {'Delta z': >{sz}s}  F"
        print(f"{'Delta = Reference - Result': ^{len(header)}s}")
        print(f"{f'! marks residuals > {f'{tolerance:.5f}'} m': ^{len(header)}s}")
        print(header)
        print("-" * len(header))
        for line_diff in diff.coordinates:
            if not show_weighted and line_diff.flag.lower() == "w":
                continue

            line = (
                f"{line_diff.station:4s} "
                f"{line_diff.x: >{sz},.5f}"
                f"{check_example.flag_if_too_high(line_diff.x, tolerance)} "
                f"{line_diff.y: >{sz},.5f}"
                f"{check_example.flag_if_too_high(line_diff.y, tolerance)} "
                f"{line_diff.z: >{sz},.5f}"
                f"{check_example.flag_if_too_high(line_diff.z, tolerance)} "
                f"{line_diff.flag} "
            )
            if substitute:
                line = line.replace("0", replacement)
            print(line)
        print()


@main.group(aliases=["dt"])
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
    print(json.dumps(gps_date.info, indent=2))


@dateinfo.command
@click.argument("week", type=int)
def gpsweek(week: int) -> None:
    """
    Show date information based on GPS week.

    """
    gps_date = dates.GPSDate.from_gps_week(week)
    print(json.dumps(gps_date.info, indent=2))


@dateinfo.command
@click.argument("year", type=int)
@click.argument("doy", type=int)
def ydoy(year: int, doy: int) -> None:
    """
    Show date information based on Year and day of year [DOY].

    """
    gps_date = dates.GPSDate.from_year_doy(year, doy)
    print(json.dumps(gps_date.info, indent=2))


def prompt_proceed() -> bool:
    return input("Proceed (y/[n]): ").lower() == "y"


@main.command
@click.option("-i", "--identifier", multiple=True, type=str, default=[], required=False)
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
def download(
    identifier: list[str], force: bool = False, campaign: str | None = None
) -> None:
    """
    Download all sources in the autobernese configuration file.

    """
    if campaign is not None:
        config = _campaign.load(campaign)
    else:
        config = configuration.load()

    sources: list[_source.Source] = config.get("sources", [])
    if not sources:
        log.debug(f"No sources found ...")
        raise SystemExit

    # Filter if asked to
    if len(identifier) > 0:
        sources = [source for source in sources if source.identifier in identifier]

    # Print preamble, before asking to proceed
    preamble = "Downloading the following sources\n"
    sz = max(len(source.identifier) for source in sources)
    preamble += "\n".join(
        f"{source.identifier: >{sz}s}: {source.description}" for source in sources
    )
    print(preamble)

    # Ask
    if not prompt_proceed():
        raise SystemExit

    # Resolve sources
    s = "s" if len(sources) > 1 else ""
    msg = f"Resolving {len(sources)} source{s} ..."
    log.info(msg)

    source: _source.Source
    status_total: DownloadStatus = DownloadStatus()
    for source in sources:
        msg = f"Download: {source.identifier}: {source.description}"
        print(f"[black on white]{msg}[/]")
        log.info(msg)

        if force:
            source.max_age = 0

        if source.protocol == "ftp":
            status = ftp.download(source)
            status_total += status

        elif source.protocol in ("http", "https"):
            status = http.download(source)
            status_total += status

        elif source.protocol == "file":
            status = file.download(source)
            status_total += status

        print(asdict(status))

    else:
        msg = "Finished downloading sources ..."
        print(msg)
        log.debug(msg)

        print(f"Overall status:")
        print(asdict(status_total))


@main.group(invoke_without_command=True, aliases=["c"])
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
    # print("\n".join(_campaign.ls(verbose)))
    campaign_infos = _campaign.ls(verbose)
    # print(json.dumps([asdict(ci) for ci in campaign_infos]))
    fstr = "{directory: <40s} {size: >10s} {template} {version} {username} {created}"
    lines = []
    for campaign_info in campaign_infos:
        kwargs = {
            **asdict(campaign_info),
            **{"size": humanize.naturalsize(campaign_info.size, binary=True)}
        }
        lines.append(fstr.format(**kwargs))
    print("\n".join(lines))


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
    sources: list[_source.Source] | None = _campaign.load(name).get("sources", [])

    if not sources:
        msg = f"No sources found"
        print(msg)
        log.info(msg)
        return

    formatted = (
        f"""\
{source.identifier=}
{source.url=}
{source.destination=}
{source.protocol=}
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
@click.option("--verbose", "-v", is_flag=True, help="Print realised task data.")
def tasks(name: str, verbose: bool) -> None:
    """
    Show tasks for a campaign.

    """
    tasks: list[_task.Task] | None = _campaign.load(name).get("tasks")

    if tasks is None:
        msg = f"No tasks found"
        print(msg)
        log.info(msg)
        return

    if not verbose:
        for task in tasks:
            print(task)
            print()
        return

    for task in tasks:
        for resolved in task.resolve():
            print(json.dumps(resolved, indent=2))
            print()


@campaign.command
@click.argument("campaign_name", type=str)
@click.option("-i", "--identifier", multiple=True, type=str, default=[], required=False)
def run(campaign_name: str, identifier: list[str]) -> None:
    """
    Resolve and run all or specified campaign tasks.

    """
    try:
        tasks: list[_task.Task] | None = _campaign.load(campaign_name).get("tasks")
    except RuntimeError as e:
        print(e)
        raise SystemExit

    if tasks is None:
        msg = f"No tasks found"
        print(msg)
        log.info(msg)
        return

    print_versions()

    if len(identifier) > 0:
        tasks = [task for task in tasks if task.identifier in identifier]

    print("Running the following tasks in the campaign configuration file")
    sz = max(len(task.identifier) for task in tasks)
    print(
        "\n".join(
            f"{task.identifier: >{sz}s}: {len(task.runners()): >3d} unique combinations"
            for task in tasks
        )
    )
    proceed = input("Proceed (y/[n]): ").lower() == "y"
    if not proceed:
        raise SystemExit

    runner: _task.TaskRunner
    for task in tasks:
        msg = f"Running combinations for {type(task).__qualname__} instance with ID {task.identifier!r}"
        log.info(msg)
        print(f"[black on white][AutoBernese]: {msg}[/]")

        try:
            for runner in task.runners():
                msg = f"BPE task ID: {runner.arguments.get('taskid')}"
                log.info(msg)
                print(f"[black on white][AutoBernese]: {msg}[/]")
                terminal_output = runner.run()
                print(terminal_output)
                print("")

        except KeyboardInterrupt:
            log.info(
                "Asking user to continue or completely exit from list of campaign tasks."
            )
            exit_confirmed = input(
                "Do you want to exit completely ([y]/n)"
            ).lower() in ("", "y")
            if exit_confirmed:
                log.info(
                    "User confirmed breaking the execution of the remaining campaign tasks."
                )
                break


# @campaign.command
# @click.argument("campaign_name", type=str)
# @click.option("-i", "--identifier", multiple=True, type=str, default=[], required=False)
# def clean_bpe_output(campaign_name: str, identifier: list[str]) -> None:
#     """
#     Delete content of the BPE directory of the given campaign.

#     """
#     _dir = _campaign._campaign_dir(campaign_name)
#     dir_bpe = _dir / "BPE"

#     if len(identifier) > 0:
#         fnames = []
#         for ident in identifier:
#             fnames.extend(list(dir_bpe.glob("{ident}*.*")))
#     else:
#         fnames = list(dir_bpe.glob("*.LOG"))
#         fnames.extend(list(dir_bpe.glob("*.PRT")))

#     print(fnames)
#     print(len(fnames))

#     # for fname in fnames:
#     #     fname.unlink()


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
@click.option(
    "-C",
    "--campaign",
    help="Campaign-specific station data.",
    required=False,
)
def sitelogs2sta(
    config: Path,
    sitelogs: tuple[Path],
    individually_calibrated: tuple[str],
    output_filename: Path,
    campaign: str | None = None,
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

    4.  Supply campaign name to create a STA file from standard settings in
        campaign-specific configuration.

    """
    arguments: dict[str, Any] | None = None
    if config is not None:
        log.info(f"Create STA file from arguments in given input-file.")
        arguments = configuration.with_env(config)

    elif sitelogs:
        log.info(f"Create STA file from given arguments.")
        arguments = dict(
            sitelogs=list(sitelogs),
            individually_calibrated=individually_calibrated,
            output_sta_file=output_filename,
        )

    elif campaign is not None:
        log.info(f"Create STA file from arguments in campaign-specific configuration.")
        arguments = _campaign.load(campaign).get("station")

    elif configuration.load().get("station") is not None:
        log.info(f"Create STA file from arguments in the configuration.")
        arguments = configuration.load().get("station")

    if arguments is None:
        msg = f"No tasks found"
        print(msg)
        log.info(msg)
        return
    sta.create_sta_file_from_sitelogs(**arguments)


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
def build(ipath: str, opath: str, beg: dt.date | None, end: dt.date | None) -> None:
    """
    Concatenate hour files (`H%H`) with troposphere delay model into dayfiles.

    Build day file for each date for which there is data available.

    """
    msg = f"Build VMF3 files for chosen interval {beg} to {end} ..."
    log.info(msg)
    print(msg)
    for vmf_file in vmf.vmf_files(ipath, opath, beg, end):
        msg = f"Building {vmf_file.output_file} ..."
        log.info(msg)
        print(msg, end=" ")

        build_msg = vmf_file.build()
        if build_msg:
            print("[red]FAILED[/red]")
            print(f"  Error: {build_msg}")
            continue

        print("[green]SUCCESS[/green]")


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
    Show status for possible VMF3 dates.

    Return status for each date for which there should be data available.

    """
    msg = f"Get VMF3 file status for files in chosen interval {beg} to {end} ..."
    log.info(msg)
    print(msg)
    print([vmf_file.status() for vmf_file in vmf.vmf_files(ipath, opath, beg, end)])
