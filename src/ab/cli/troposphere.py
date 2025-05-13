"""
Command-line interface for troposphere delay model data

"""

import logging
from pathlib import Path
import datetime as dt
from dataclasses import (
    dataclass,
)

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print

from ab.cli import (
    _input,
)
from ab import (
    configuration,
    vmf,
)


log = logging.getLogger(__name__)


@click.group(cls=ClickAliasedGroup)
def troposphere() -> None:
    """
    Stand-alone tools for troposphere-delay model data (VMF3).

    """


@dataclass
class CLITroposphereInput:
    ipath: Path
    opath: Path
    beg: dt.date
    end: dt.date


def __get_troposphere_args(
    ipath: Path | None, opath: Path | None, beg: dt.date | None, end: dt.date | None
) -> CLITroposphereInput:
    if ipath is None:
        c_tro = configuration.load().get("troposphere")
        if c_tro is None:
            raise SystemExit(
                f"Missing section `troposphere` from common configuration."
            )
        ipath = c_tro.get("ipath")
        if c_tro is None:
            raise SystemExit(
                f"Missing input-path section `ipath` from `troposphere` section."
            )

    if opath is None:
        c_tro = configuration.load().get("troposphere")
        if c_tro is None:
            raise SystemExit(
                f"Missing section `troposphere` from common configuration."
            )
        opath = c_tro.get("opath")
        if c_tro is None:
            raise SystemExit(
                f"Missing output-path section `opath` from `troposphere` section."
            )

    if beg is None:
        beg = dt.date.today()

    if end is None:
        end = beg + dt.timedelta(days=1)

    return CLITroposphereInput(ipath, opath, beg, end)


@troposphere.command
# @click.option(
#     "-i",
#     "--ipath",
#     type=str,
# )
# @click.option(
#     "-o",
#     "--opath",
#     type=str,
# )
@click.option(
    "-b",
    "--beg",
    type=_input.date,
    help=f"Format: {_input.DATE_FORMAT}",
)
@click.option(
    "-e",
    "--end",
    type=_input.date,
    help=f"Format: {_input.DATE_FORMAT}",
)
def build(beg: dt.date | None, end: dt.date | None) -> None:
    """
    Concatenate hour files (`H%H`) into dayfiles.

    Build day file for each date for which there is data available.

    """
    ipath: Path | None = None
    opath: Path | None = None
    args = __get_troposphere_args(ipath, opath, beg, end)
    log.info(f"Build VMF3 files for chosen interval {args.beg} to {args.end} ...")
    for builder in vmf.day_file_builders(args.ipath, args.opath, args.beg, args.end):
        msg = f"Building {builder.dayfile} ..."
        log.info(msg)
        print(msg, end=" ")
        build_msg = builder.build()
        if build_msg:
            print("[red]FAILED[/red]")
            print(f"  Error: {build_msg}")
            continue
        print("[green]SUCCESS[/green]")


@troposphere.command
@click.option(
    "-b",
    "--beg",
    type=_input.date,
    help=f"Format: {_input.DATE_FORMAT}",
)
@click.option(
    "-e",
    "--end",
    type=_input.date,
    help=f"Format: {_input.DATE_FORMAT}",
)
def test(beg: dt.date | None, end: dt.date | None) -> None:
    """
    Concatenate hour files (`H%H`) into dayfiles.

    Build day file for each date for which there is data available.

    """
    ipath: Path | None = None
    opath: Path | None = None
    args = __get_troposphere_args(ipath, opath, beg, end)
    log.info(f"Test VMF3 files for chosen interval {args.beg} to {args.end} ...")
    for builder in vmf.day_file_builders(args.ipath, args.opath, args.beg, args.end):
        msg = f"Testing {builder.dayfile} ..."
        log.info(msg)
        print(msg, end=" ")
        test_msg = builder.test()
        if test_msg:
            print("[red]FAILED[/red]")
            print(f"  Error: {test_msg}")
            continue
        print("[green]SUCCESS[/green]")


@troposphere.command
# @click.option(
#     "-i",
#     "--ipath",
#     type=str,
# )
# @click.option(
#     "-o",
#     "--opath",
#     type=str,
# )
@click.option(
    "-b",
    "--beg",
    type=_input.date,
    help=f"Format: {_input.DATE_FORMAT}",
)
@click.option(
    "-e",
    "--end",
    type=_input.date,
    help=f"Format: {_input.DATE_FORMAT}",
)
def status(beg: dt.date | None, end: dt.date | None) -> None:
    """
    Print availability of hour and day files in selected interval.

    """
    ipath: Path | None = None
    opath: Path | None = None
    args = __get_troposphere_args(ipath, opath, beg, end)
    log.info(
        f"Get VMF3 file status for files in chosen interval {args.beg} to {args.end} ..."
    )
    print(
        [
            vmf_file.status()
            for vmf_file in vmf.day_file_builders(
                args.ipath, args.opath, args.beg, args.end
            )
        ]
    )
