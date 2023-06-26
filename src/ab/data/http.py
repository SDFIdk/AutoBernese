"""
Module for downloading files over HTTP.

"""
from pathlib import Path
import logging

import requests

from ab.data import DownloadStatus
from ab.data.source import Source
from ab.data.stats import already_updated


log = logging.getLogger(__name__)


_SESSION: requests.Session = None


def get_session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
    return _SESSION


def download(source: Source) -> DownloadStatus:
    """
    Download a file over HTTP (TLS or not)

    """
    status = DownloadStatus()
    for pair in source.resolve():
        destination = Path(pair.path_local)
        destination.mkdir(parents=True, exist_ok=True)
        ofname = destination / pair.fname
        if already_updated(ofname, max_age=source.max_age):
            log.debug(f"{ofname.name} already downloaded ...")
            status.existing += 1
            continue
        log.info(f"Download {pair.uri} to {ofname} ...")
        r = get_session().get(pair.uri, allow_redirects=True, timeout=30)
        ofname.write_bytes(r.content)
        status.downloaded += 1
    return status
