"""
Command-line interface for downloading external and local data sources

"""

import logging
from types import ModuleType
from dataclasses import asdict

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box

from ab.cli import (
    _input,
    _filter,
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
    Download all sources in the AutoBernese configuration file.

    """
    if campaign is not None:
        config = _campaign.load(campaign)
    else:
        config = configuration.load()

    # Load raw configuration items
    raw_sources = _filter.get_raw(config, "sources", identifier)

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

    # Print preamble, before asking to proceed
    # preamble = "Downloading the following sources\n"
    # sz = max(len(source.identifier) for source in sources)
    # preamble += "\n".join(
    #     f"{source.identifier: >{sz}s}: {source.description}" for source in sources
    # )
    # print(preamble)
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

    # Ask
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

    with Live(table, console=console, screen=False, refresh_per_second=20):

        status_total: TransferStatus = TransferStatus()
        for source in sources:
            msg = f"Download: {source.identifier}: {source.description}"
            log.info(msg)
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

    # status_total: TransferStatus = TransferStatus()
    # for source in sources:
    #     msg = f"Download: {source.identifier}: {source.description}"
    #     print(f"[black on white]{msg}[/]")
    #     log.info(msg)
    #     agent = PROTOCOLS[source.protocol]
    #     status = agent.download(source)
    #     status_total += status
    #     print(asdict(status))

    # else:
    #     msg = "Finished downloading sources ..."
    #     print(f"\n{msg}")
    #     log.debug(msg)
    #     print(f"Overall status:")
    #     print(asdict(status_total))
