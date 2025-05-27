"""
Download [i.e. copy] local files.

"""

from pathlib import Path
import shutil
import logging
from typing import Iterable

from ab import configuration
from ab.paths import resolve_wildcards
from ab.data import DownloadStatus
from ab.data.source import Source
from ab.data.stats import already_updated


log = logging.getLogger(__name__)


def download(source: Source) -> DownloadStatus:
    """
    Download local paths resolved from a Source instance.

    """
    status = DownloadStatus()

    for pair in source.resolve():
        destination = Path(pair.path_local)
        destination.mkdir(parents=True, exist_ok=True)

        # Loop over each file resolved
        for ifname in resolve_wildcards(pair.uri):
            ofname = destination / ifname.name

            if not ifname.is_file():
                log.warning(f"File {ifname!r} not found ...")
                status.not_found += 1
                continue

            if already_updated(ofname, max_age=source.max_age):
                log.debug(f"{ofname.name!r} already downloaded ...")
                status.existing += 1
                continue

            log.info(f"Copy {ifname} to {ofname} ...")
            shutil.copy2(ifname, ofname)

            if not ofname.is_file():
                log.warning(f"File {ofname.name!r} not copied ...")
                status.failed += 1
                continue

            status.downloaded += 1

    return status
