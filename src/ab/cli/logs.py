"""
Command-line interface for seeing the log file

"""

import logging
import subprocess as sub

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print

from ab import configuration


log = logging.getLogger(__name__)


@click.command
def logs() -> None:
    """
    Follow log file (run `tail -f path/to/logfile.log`).

    """
    runtime = configuration.load().get("runtime")
    if runtime is None:
        raise SystemExit(f"No runtime entry found in configuration.")
    filename = runtime.get("logging", {}).get("filename")
    if filename is None:
        raise SystemExit(f"No log-file name entry found in logging configuration.")

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
