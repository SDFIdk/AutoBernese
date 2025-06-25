"""
Command-line interface for station sitelogs and STA files

"""

import logging
from pathlib import Path
from typing import Any

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print

from ab import (
    configuration,
    dates,
)
from ab.bsw import campaign as _campaign
from ab.station import sta


log = logging.getLogger(__name__)


@click.group(cls=ClickAliasedGroup)
def station() -> None:
    """
    Stand-alone tools for station data.

    """


@station.command
@click.option(
    "-c",
    "--campaign",
    "name",
    required=False,
    default=None,
    type=str,
    help="Campaign-specific station data.",
)
@click.option(
    "-f",
    "--config",
    required=False,
    default=None,
    type=Path,
    help="Path to an input YAML file with valid `station`.",
)
@click.option(
    "-i",
    "sitelogs",
    multiple=True,
    type=Path,
    help="One or more paths to site-log files to build the STA-file from.",
)
@click.option(
    "-k",
    "individually_calibrated",
    multiple=True,
    type=str,
    help="Four-letter ID for each station that is individually calibrated.",
)
@click.option(
    "-o",
    "output_filename",
    required=False,
    default=Path(".").resolve() / "sitelogs.STA",
    type=Path,
    help="Path to optional output path and filename for the STA file.",
)
def sitelogs2sta(
    name: str,
    config: Path,
    sitelogs: tuple[Path],
    individually_calibrated: tuple[str],
    output_filename: Path,
) -> None:
    """
    Create a STA file from sitelogs and optional station information.

    Choose one of the following ways to run it:

    1.  No arguments: Use input provided in common user configuration
        (`autobernese.yaml`).

    2.  Use the flag `-c` to suppply a name for a campaign whose configuration
        (`campaign.yaml`) contains to create a STA file from standard settings
        in campaign-specific configuration.

    2.  Use the flag `-f` to supply a path to a custom path to a YAML file with
        arguments.

    4.  Use flags `-i`, `-k` and `-o` to supply needed and optional arguments on
        the command line.


    The following arguments are possible:

    \b
    *   Site-log filenames are required.
    *   Four-letter IDs for individually-calibrated stations are optional.
    *   The path to the output STA file is optional. (Default: `sitelogs.STA`)

    These arguments can be provided in a configuration file which has the
    following structure:

    \b
    ```yaml
    station:
      sitelogs: [sta1.log, sta2.log]
      individually_calibrated: [sta1]
      output_sta_file: /path/to/output.STA
    ```

    Provided configuration files are loaded with the current Bernese
    environment, so advanced paths are possible, e.g.

    \b
    ```yaml
    sitelogs: !Path [*D, sitelogs, '*.log']
    ```

    which will give a sequence of all the files ending with `log` in the given
    directory.

    \b
    ```yaml
    sitelogs:
    - !Path [*D, sitelogs, 'sta1*.log']
    - !Path [*D, sitelogs, 'sta2*.log']
    - !Path [*D, sitelogs, 'sta3*.log']
    ```

    which will let you create the sequence of filenames yourself when you want
    to specifiy specific stations. The wildcard `*` lets you avoid having to
    look up the date, when the file was last updated.

    For the output STA file, you can also write the following:

    \b
    ```yaml
    output_sta_file: `!Path [*D, station, sitelogs.STA]`
    ```

    """
    arguments: dict[str, Any] | None = None
    if config is not None:
        ifname = config.absolute()
        msg = f"Create STA file with arguments in file {ifname} ..."
        log.info(msg)
        print(msg)
        arguments = configuration.load(ifname).get("station")
        print(arguments)

    elif sitelogs:
        log.info(f"Create STA file from given arguments ...")
        arguments = dict(
            sitelogs=list(sitelogs),
            individually_calibrated=individually_calibrated,
            output_sta_file=output_filename,
        )

    elif name is not None:
        msg = f"Create STA file from arguments in configuration for campaing {name} ..."
        log.info(msg)
        print(msg)
        arguments = _campaign.load(name).get("station")

    elif configuration.load().get("station") is not None:
        msg = f"Create STA file from arguments in the common user configuration `autobernese.yaml` ..."
        log.info(msg)
        print(msg)
        arguments = configuration.load().get("station")

    if arguments is None:
        msg = f"No arguments found ..."
        print(msg)
        log.info(msg)
        return

    msg = f"Creating STA file from arguments {arguments!r} ..."
    log.info(msg)
    print(msg)
    sta.create_sta_file_from_sitelogs(**arguments)
