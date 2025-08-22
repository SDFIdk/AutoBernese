"""
Command-line interface for downloading external and local data sources

"""

import logging
from types import ModuleType
from dataclasses import asdict

import click
from click_aliases import ClickAliasedGroup
from rich import print
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box

from ab.cli import (
    _input,
    _filter,
    _options,
)
from ab import configuration
from ab.configuration import sources as _sources
from ab.bsw import campaign as _campaign
from ab.data import (
    TransferStatus,
    ftp as _ftp,
    http as _http,
    file as _file,
)


log = logging.getLogger(__name__)


PROTOCOLS: dict[str, ModuleType] = dict(
    ftp=_ftp,
    http=_http,
    https=_http,
    file=_file,
)


@click.command
@_options.identifiers
@_options.exclude
@_options.force
@_options.campaign
@_options.yes
def download(
    identifiers: list[str] | None,
    exclude: list[str] | None = None,
    force: bool = False,
    name: str | None = None,
    yes: bool = False,
) -> None:
    """
    Download sources in common or campaign configuration file.

    """
    if name is not None:
        log.info(f"Using campaign configuration from {name} ...")
        config = _campaign.load(name)
    else:
        log.info(f"Using default configuration ...")
        config = configuration.load()

    # Load raw configuration items
    raw_sources = _filter.get_raw(config, "sources", identifiers, exclude)

    if not raw_sources:
        msg = f"No sources matching selected identifiers ..."
        print(msg)
        log.debug(msg)
        return

    # Build instances
    sources = _sources.load_all(raw_sources)

    # Remove sources with an unsupported protocol
    sources = [source for source in sources if source.protocol in PROTOCOLS]

    if not sources:
        msg = f"No sources with supported protocols ..."
        print(msg)
        log.debug(msg)
        return

    # Preamble
    table = Table(title="Downloading the following sources", box=box.HORIZONTALS)
    table.add_column("Identifier", no_wrap=True)
    table.add_column("Description")
    table.add_column("Local resolution count", justify="right")
    for source in sources:
        table.add_row(
            source.identifier,
            source.description,
            str(len(source.resolve())),
        )
    console = Console()
    console.print(table)

    # Ask to proceed or not
    if not _input.prompt_proceed():
        return

    # Resolve sources
    s = "s" if len(sources) > 1 else ""
    msg = f"Resolving {len(sources)} source{s} ..."
    log.info(msg)

    # Set force attribute
    if force:
        for source in sources:
            source.max_age = 0

    # Prepare output layout
    table = Table(title="Transfer Status", box=box.HORIZONTALS)
    table.add_column("Identifier", no_wrap=True)
    table.add_column("Proto")
    for key in asdict(TransferStatus()):
        table.add_column(key, justify="right")

    with Live(table, console=console, screen=False, refresh_per_second=4) as live:

        status_total: TransferStatus = TransferStatus()
        for source in sources:
            msg = f"Download: {source.identifier}: {source.description}"
            log.info(msg)
            # live.console.print(msg)

            agent = PROTOCOLS[source.protocol]
            status = agent.download(source)
            status_total += status

            args = [source.identifier, source.protocol] + [
                f"{total}" for total in asdict(status).values()
            ]
            table.add_row(*args)

        else:
            log.debug("Finished downloading sources ...")
            # Add a line and print the totals
            table.add_section()
            args = ["", ""] + [f"{total}" for total in asdict(status_total).values()]
            table.add_row(*args)
