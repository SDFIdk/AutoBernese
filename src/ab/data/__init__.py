"""
Module for downloading source data

"""
import datetime as dt
from dataclasses import dataclass
from typing import Any
from ftplib import FTP
from pathlib import Path
import logging
from urllib.parse import (
    urlparse,
    ParseResult,
)

import requests


log = logging.getLogger(__name__)


# _SESSIONS: dict[str, requests.Session | FTP] = {}


# def get_session(which: requests.Session | FTP, call_sign: str) -> requests.Session | FTP:
#     global _SESSIONS
#     if call_sign not in _SESSIONS:
#         _SESSIONS[call_sign] = which()


@dataclass
class Source:
    name: str
    url: str | Path
    destination: str | Path
    parameters: dict[str, Any]
    filenames: list[str | Path]

    _session: requests.Session | FTP = None

    @property
    def session(self) -> requests.Session | FTP:
        ...

    def download(self):
        ...


def http_download(
    domain: str, remotepath: Path, localpath: Path, *, call_sign="Odyssey"
) -> None:
    """
    Download a file over HTTP (TLS or no)

    """
    url = f"{domain}{remotepath}"
    ofname = localpath / remotepath.name
    log.info(f"Download {url} to {ofname}...")
    r = requests.get(url, allow_redirects=True, timeout=30)
    ofname.write_bytes(r.content)


def date_changed(fname: Path | str) -> dt.date:
    raw = Path(fname).stat().st_ctime
    return dt.datetime.fromtimestamp(raw).date()


def already_downloaded(fname: Path) -> bool:
    return fname.is_file() and date_changed(fname) == dt.date.today()


def ftp_download(
    domain: str, remotepath: Path, ofname: Path, *, force=False, call_sign="Aquarius"
) -> None:
    """
    Handles FTP (insecure) and FTPS downloads using anonymous user.

    """
    if already_downloaded(ofname) and not force:
        log.debug(f"{ofname.name} already downloaded today ...")
        return
    with FTP(domain) as ftp:
        ftp.login()
        ftp.cwd(f"{remotepath.parent}")
        ftp.retrbinary(f"RETR {remotepath.name}", ofname.write_bytes)


def ftp_list_files(parsed: ParseResult) -> list[str]:
    """
    List files in given location.

    """
    log.debug(f"List files in FTP directory {parsed.netloc}{parsed.path} ...")
    with FTP(parsed.netloc) as ftp:
        ftp.login()
        ftp.cwd(parsed.path)
        is_file = lambda candidate: ftp.nlst(candidate) == [candidate]
        return [candidate for candidate in ftp.nlst() if is_file(candidate)]


def download(sources) -> None:
    """
    Download specified sources.

    Handles the following input:

    *   Given a source directory, all files (no sub directories) are downloaded
        to the destination directory. The latter may have a different name.

        -   For FTP, the the sign that all files in the directory are to be
            downloaded is given with a trailing forward slash `/` in the source
            URL.

    *   Given a source file, the destination directory is also seen as
        completely specified in that the file is simply put into the destination
        directory.

    To implement:

    *   Given a source with a matrix of parameters, the parameters are read of
        and the matrix generated from the source specification.

    *   What if the year or similar is a range?

    *   What if the year or similar is given as an open range in the sense that
        all subsequent data, if available, should be downloaded?

    """
    for source in sources:
        log.debug(f"Download source specification: {source['name']}")

        parsed: ParseResult = urlparse(source["url"])

        # print(parsed)
        source_is_directory = parsed.path.endswith("/")
        # TODO: Rename paths path and dest to remote and local dir.
        path = Path(parsed.path)
        dest = Path(source.get("destination"))

        if source_is_directory:
            dest.mkdir(parents=True, exist_ok=True)
            if source.get('filenames'):
                # Get specified files
                filenames = source.get('filenames')
            else:
                # Get all files
                filenames = ftp_list_files(parsed)

            # Build full paths to individual source and destination files
            ifnames = (path / fname for fname in filenames)
            ofnames = (dest / fname for fname in filenames)

            # Get the files
            for ifname, ofname in zip(ifnames, ofnames):
                log.debug(f"Download {ifname}")
                # TODO: Check protocol
                ftp_download(
                    parsed.netloc,
                    ifname,
                    ofname,
                )
            continue

        # TODO: Reconsider assumption
        # Assume that the destination is a directory
        ofname = dest / Path(source["url"]).name

        match parsed.scheme:
            case "http" | "https":
                http_download(
                    parsed.netloc,
                    path,
                    ofname,
                )
            case "ftp":
                ftp_download(
                    parsed.netloc,
                    path,
                    ofname,
                )

    log.debug("Finished downloading sources")
