"""
Command-line interface for downloading external data

"""

import logging
from types import ModuleType
from dataclasses import (
    asdict,
)

import click
from click_aliases import ClickAliasedGroup  # type: ignore
from rich import print

from ab.cli import (
    _input,
)
from ab import (
    configuration,
)
from ab.bsw import (
    campaign as _campaign,
)
from ab.data import (
    DownloadStatus,
    source as _source,
    ftp,
    http,
    file,
)


log = logging.getLogger(__name__)


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
    Download all sources in the autobernese configuration file.

    """
    if campaign is not None:
        config = _campaign.load(campaign)
    else:
        config = configuration.load()

    sources: list[_source.Source] = config.get("sources", [])
    if not sources:
        msg = f"No sources found in configuration ..."
        print(msg)
        log.debug(msg)
        raise SystemExit

    # Filter if asked to
    if len(identifier) > 0:
        sources = [source for source in sources if source.identifier in identifier]

    # Check again after filtering
    if not sources:
        msg = f"No sources matching selected identifiers ({', '.join(identifier)}) ..."
        print(msg)
        log.debug(msg)
        raise SystemExit

    # Print preamble, before asking to proceed
    preamble = "Downloading the following sources\n"
    sz = max(len(source.identifier) for source in sources)
    preamble += "\n".join(
        f"{source.identifier: >{sz}s}: {source.description}" for source in sources
    )
    print(preamble)

    # Ask
    if not _input.prompt_proceed():
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

        agent: ModuleType
        if source.protocol == "ftp":
            agent = ftp
        elif source.protocol in ("http", "https"):
            agent = http
        elif source.protocol == "file":
            agent = file

        status = agent.download(source)
        status_total += status

        print(asdict(status))

    else:
        msg = "Finished downloading sources ..."
        print(msg)
        log.debug(msg)

        print(f"Overall status:")
        print(asdict(status_total))
