"""
Command-line interface for troposphere-delay model data

"""

import os
import datetime as dt
from pathlib import Path
from functools import (
    partial,
    wraps,
)
from dataclasses import dataclass
import logging
from typing import Final
import multiprocessing as mp

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print

from ab.cli import _options
from ab import (
    configuration,
    vmf,
)
from ab.dates import gps_week_limits


log = logging.getLogger(__name__)


N_CPUS: Final = len(os.sched_getaffinity(0))


@click.group(cls=ClickAliasedGroup)
def troposphere() -> None:
    """
    Stand-alone tools for troposphere-delay model data (VMF3).

    """


@dataclass
class CLITroposphereInput:
    ipath: Path | str
    opath: Path | str
    beg: dt.date
    end: dt.date
    ifname: Path | str
    ofname: Path | str


def parse_args(
    ipath: str | None,
    opath: str | None,
    gps_week: int | None,
    beg: dt.date | None,
    end: dt.date | None,
    ifname: str | None,
    ofname: str | None | None,
) -> CLITroposphereInput:
    """
    Parse generic input from command-line interface and set missing data.

    """
    section = configuration.load().get("troposphere")

    # Core configuration has this section; common configuration may update it ...
    assert section is not None

    ipath = ipath or section.get("ipath")
    if ipath is None:
        raise SystemExit(f"Missing input-path from command or configuration ...")

    opath = opath or section.get("opath")
    if opath is None:
        raise SystemExit(f"Missing output-path from command or configuration ...")

    if gps_week is not None:
        beg, end = gps_week_limits(gps_week)

    if beg is None:
        beg = section.get("beg") or dt.date.today()

    if end is None:
        end = section.get("end") or beg + dt.timedelta(days=1)

    ifname = ifname or section.get("ifname")
    if ifname is None:
        raise SystemExit(f"Missing hour-file format from command or configuration ...")

    ofname = ofname or section.get("ofname")
    if ofname is None:
        raise SystemExit(f"Missing day-file format from command or configuration ...")

    raw = CLITroposphereInput(ipath, opath, beg, end, ifname, ofname)
    log.info(f"Run using the following input: {raw} ...")
    return raw


def common_options(func):
    """
    A single decorator for common options

    Source: https://stackoverflow.com/a/70852267

    """

    @_options.ipath
    @_options.opath
    @_options.gps_week
    @_options.beg
    @_options.end
    @_options.hour_file_format
    @_options.day_file_format
    @wraps(func)
    def wrapper_common_options(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper_common_options


def cli_wrapper(builder: vmf.DayFileBuilder, method: str, action: str) -> None:
    """
    Single-process executor which prints status to the terminal

    """
    msg = f"{action}ing {builder.day_file} ..."
    log.info(msg)
    failed_msg = getattr(builder, method)()
    if failed_msg:
        print(f"{msg} [red]FAILED[/red]")
        print(f"  Error: {failed_msg}")
    print(f"{msg} [green]SUCCESS[/green]")


def dispatch(
    args: CLITroposphereInput, method: str, action: str, *, timeout: float = 1
) -> None:
    log.info(f"{action} VMF files for chosen interval {args.beg} to {args.end} ...")
    builders = vmf.day_file_builders(
        args.ipath, args.opath, args.beg, args.end, args.ifname, args.ofname
    )
    wrappers = [partial(cli_wrapper, builder, method, action) for builder in builders]
    try:
        with mp.Pool(processes=N_CPUS) as pool:
            multiple_results = [pool.apply_async(wrapper) for wrapper in wrappers]
            [res.get(timeout=timeout) for res in multiple_results]
    except KeyboardInterrupt:
        msg = f"{action} interrupted by user ..."
        log.info(msg)
        print(msg)


@troposphere.command
@common_options
def build(
    ipath: str | None,
    opath: str | None,
    gps_week: int | None,
    beg: dt.date | None,
    end: dt.date | None,
    ifname: str | None,
    ofname: str | None,
) -> None:
    """
    Concatenate hour files into day files.

    Build day file for each date for which there is data available.

    """
    args = parse_args(ipath, opath, gps_week, beg, end, ifname, ofname)
    dispatch(args, "build", "Build", timeout=10)


@troposphere.command
@common_options
def check(
    ipath: str | None,
    opath: str | None,
    gps_week: int | None,
    beg: dt.date | None,
    end: dt.date | None,
    ifname: str | None,
    ofname: str | None,
) -> None:
    """
    Check that input hour files went into built day files.

    """
    args = parse_args(ipath, opath, gps_week, beg, end, ifname, ofname)
    dispatch(args, "check", "Check", timeout=10)


@troposphere.command
@common_options
def status(
    ipath: str | None,
    opath: str | None,
    gps_week: int | None,
    beg: dt.date | None,
    end: dt.date | None,
    ifname: str | None,
    ofname: str | None,
) -> None:
    """
    Show availability of hour and day files in selected interval.

    """
    args = parse_args(ipath, opath, gps_week, beg, end, ifname, ofname)
    log.info(f"Show data status for chosen interval {args.beg} to {args.end} ...")
    builders = vmf.day_file_builders(
        args.ipath, args.opath, args.beg, args.end, args.ifname, args.ofname
    )
    try:
        with mp.Pool(processes=N_CPUS) as pool:
            multiple_results = [
                pool.apply_async(builder.status) for builder in builders
            ]
            print([res.get(timeout=1) for res in multiple_results])
    except KeyboardInterrupt:
        msg = "Status retrieval interrupted by user ..."
        log.info(msg)
        print(msg)
