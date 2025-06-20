"""
Transfer files over HTTP

"""

from pathlib import Path
import logging

import requests

from ab.data import TransferStatus
from ab.data.source import Source
from ab.data.stats import already_updated


log = logging.getLogger(__name__)


_SESSION: requests.Session | None = None


def get_session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
    return _SESSION


def download(source: Source) -> TransferStatus:
    """
    Download a file over HTTP (TLS or not)

    """
    status = TransferStatus()
    for pair in source.resolve():
        destination = Path(pair.path_local)
        destination.mkdir(parents=True, exist_ok=True)
        ofname = destination / pair.fname

        if already_updated(ofname, max_age=source.max_age):
            log.debug(f"{ofname.name} already downloaded ...")
            status.existing += 1
            continue

        log.info(f"Download {pair.uri} to {ofname} ...")
        response = get_session().get(pair.uri, allow_redirects=True, timeout=30)

        if not response.ok:
            # Calling it a failure, without knowing the cause of the error.
            status.failed += 1
            continue

        ofname.write_bytes(response.content)
        status.success += 1

    return status
