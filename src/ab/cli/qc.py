"""
Command-line interface for quality assurance and quality control

"""

import logging

import click
from click_aliases import ClickAliasedGroup
from rich import print

from ab.qaqc import check_example


log = logging.getLogger(__name__)


@click.group
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
        reference = check_example.extract_coordinates(pair.ref.read_text())
        result = check_example.extract_coordinates(pair.res.read_text())

        diff = reference - result

        print(f"Reference ({reference.date}): {pair.ref.name}")
        print(f"Result    ({result.date}): {pair.res.name}")
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
