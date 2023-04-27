"""
Module for downloading source data

"""
import datetime as dt
from dataclasses import dataclass
from typing import Any
import pathlib
from urllib.parse import (
    urlparse,
    ParseResult,
)
import ftplib
import logging

import requests

from ab.data import (
    ftp,
    http,
)


log = logging.getLogger(__name__)


def date_changed(fname: pathlib.Path | str) -> dt.date:
    raw = pathlib.Path(fname).stat().st_ctime
    return dt.datetime.fromtimestamp(raw).date()


def already_downloaded(fname: pathlib.Path) -> bool:
    return fname.is_file() and date_changed(fname) == dt.date.today()


@dataclass
class Source:
    name: str
    url: str | pathlib.Path
    destination: str | pathlib.Path
    parameters: dict[str, Any]
    filenames: list[str | pathlib.Path]

    _session: requests.Session | ftplib.FTP = None

    @property
    def session(self) -> requests.Session | ftplib.FTP:
        ...

    def download(self, ofname):
        if already_downloaded(ofname):  #  and not force:
            log.debug(f"{ofname.name} already downloaded today ...")
            return


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
        path = pathlib.Path(parsed.path)
        dest = pathlib.Path(source.get("destination"))

        if source_is_directory:
            dest.mkdir(parents=True, exist_ok=True)
            if source.get('filenames'):
                # Get specified files
                filenames = source.get('filenames')
            else:
                # Get all files
                filenames = ftp.list_files(parsed)

            # Build full paths to individual source and destination files
            ifnames = (path / fname for fname in filenames)
            ofnames = (dest / fname for fname in filenames)

            # Get the files
            for ifname, ofname in zip(ifnames, ofnames):
                log.debug(f"Download {ifname}")
                # TODO: Check protocol
                ftp.download(
                    parsed.netloc,
                    ifname,
                    ofname,
                )
            continue

        # TODO: Reconsider assumption
        # Assume that the destination is a directory
        ofname = dest / pathlib.Path(source["url"]).name

        args = (
            parsed.netloc,
            path,
            ofname,
        )
        match parsed.scheme:
            case "http" | "https":
                http.download(*args)
            case "ftp":
                ftp.download(*args)

    log.debug("Finished downloading sources")
