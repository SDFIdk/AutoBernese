"""
Module for downloading files over HTTP.

"""
import logging
from pathlib import Path

import requests

# from ab.data import Source


log = logging.getLogger(__name__)

_SESSION: requests.Session = None


def get_session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
    return _SESSION


# def download(
#     domain: str, remotepath: pathlib.Path, localpath: pathlib.Path,
# ) -> None:
def download(url: str, local_path: str) -> None:
    """
    Download a file over HTTP (TLS or not)

    """
    ofname = Path(local_path) / Path(url).name
    log.info(f"Download {url} to {ofname}...")
    r = get_session().get(url, allow_redirects=True, timeout=30)
    # TODO: Check response is OK, before saving the data
    ofname.write_bytes(r.content)
