"""
Command-line interface for downloading external and local data sources

"""

import logging
from types import ModuleType
from dataclasses import asdict

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print

from ab.cli import _input
from ab import configuration
from ab.bsw import campaign as _campaign
from ab.data import (
    TransferStatus,
    source as _source,
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

    sources: list[_source.Source] = config.get("sources", [])
    if not sources:
        msg = f"Source list empty ..."
        print(msg)
        log.debug(msg)
        return

    # Select based on identifiers, if any
    if len(identifier) > 0:
        sources = [source for source in sources if source.identifier in identifier]

    if not sources:
        msg = f"No sources matching selected identifiers ..."
        print(msg)
        log.debug(msg)
        return

    # Remove sources with an unsupported protocol
    sources = [source for source in sources if source.protocol in PROTOCOLS]

    if not sources:
        msg = f"No sources with supported protocols ..."
        print(msg)
        log.debug(msg)
        return

    # Print preamble, before asking to proceed
    preamble = "Downloading the following sources\n"
    sz = max(len(source.identifier) for source in sources)
    preamble += "\n".join(
        f"{source.identifier: >{sz}s}: {source.description}" for source in sources
    )
    print(preamble)

    # Ask
    if not _input.prompt_proceed():
        return

    # Resolve sources
    s = "s" if len(sources) > 1 else ""
    msg = f"Resolving {len(sources)} source{s} ..."
    log.info(msg)

    # Set force attribute
    source: _source.Source
    if force:
        for source in sources:
            source.max_age = 0

    status_total: TransferStatus = TransferStatus()
    for source in sources:
        msg = f"Download: {source.identifier}: {source.description}"
        print(f"[black on white]{msg}[/]")
        log.info(msg)
        agent = PROTOCOLS[source.protocol]
        status = agent.download(source)
        status_total += status
        print(asdict(status))

    else:
        msg = "Finished downloading sources ..."
        print(f"\n{msg}")
        log.debug(msg)
        print(f"Overall status:")
        print(asdict(status_total))
