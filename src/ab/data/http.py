"""
Module for downloading files over HTTP.

"""
import logging
import pathlib

import requests


log = logging.getLogger(__name__)

_SESSION: requests.Session = None
_HEADERS: dict[str, str] = dict(

)


def get_session(headers: dict[str, str] = None) -> requests.Session:
    global _SESSION, _HEADERS
    if _SESSION is None and headers is None:
        _SESSION = requests.Session(headers={**_HEADERS, **headers})
    return _SESSION


def download(
    domain: str, remotepath: pathlib.Path, localpath: pathlib.Path,
) -> None:
    """
    Download a file over HTTP (TLS or no)

    """
    url = f"{domain}{remotepath}"
    ofname = localpath / remotepath.name
    log.info(f"Download {url} to {ofname}...")
    r = get_session().get(url, allow_redirects=True, timeout=30)
    ofname.write_bytes(r.content)
