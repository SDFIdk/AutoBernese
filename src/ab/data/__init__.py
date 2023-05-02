"""
Module for downloading source data

"""
from os.path import join
import datetime as dt
from typing import (
    Any,
    Iterable,
)
from pathlib import Path
from urllib.parse import (
    urlparse,
    ParseResult,
)
from fnmatch import fnmatch
from ftplib import FTP
import logging

import requests

from ab.data.source import Source


log = logging.getLogger(__name__)


# Local files
def date_changed(fname: Path | str) -> dt.date:
    raw = Path(fname).stat().st_ctime
    return dt.datetime.fromtimestamp(raw).date()


def already_downloaded(fname: Path) -> bool:
    return fname.is_file() and date_changed(fname) == dt.date.today()


# API access point
def download(sources) -> None:
    """
    Download specified sources asumed to be instances of Source.

    A source is a source and not a downloader. The source can yield a list of
    files to download if any filenames are specified.

    A Source instance can tell what method (scheme in URL language) is used so
    that the user can use the right tool to get the source.

    TODO: Split source and URI resolution from how it is obtained and in what
    way. Source may not be the best name, since it contains information about
    the corresponding file destination(s).

    A Source instance handles the following input:

    *   The destination is always assumed to be a directory in which to store
        the downloaded files given their resolved paths.

        -   Given a source file, the destination directory is also seen as
            completely specified in that the file is simply put into the
            destination directory.

    *   If the source URL points to a directory, all files (no sub directories)
        within this directory are downloaded to the destination directory. The
        destination directory may have a different name.

        -   <del>For FTP, the the sign that all files in the directory are to be
            downloaded is given with a trailing forward slash `/` in the source
            URL.</del>

        -   The signal that the entire FTP directory should be downloaded is
            that there are no specific filenames given.

    *   Given a source with a dictionary of parameters, a list of dictionaries
        with each parameter-combination (one value for each parameter) is
        generated, and the source may thereby have many paths for the server.

        -   If filenames are given, they are added to each resolved path.

    *   Any filenames specified are resolved in the following manner:

        -   If there are more paths given a set of parameters, the specified
            source files are downloaded for each of the paths resolved.

        -   Filenames may contain UNIX wildcard patterns as can be matched
            against using Python's fnmatch module.

    Questions:

    *   Where to add the final URL parsing that will give the host/domain, path
        to download from?

    *   How to best return an interable of the remote and local filepaths to the
        user?

        -   For HTTP, this is easy, since the paths can be completely specified
            from the beginning, as they should be known in advance, since there
            is no way of listing a directory for the one HTTP source we have so
            far.

            For HTTP, there is no need to split the URL up into smaller parts
            (host, path, filename).

        -   For FTP, the need for downloading data using wildcard characters,
            means that the filenames must come from an active connection to the
            FTP-server so that the directory listing can be obtained, and, here,
            the filenames are used without their full path, since the protocol
            forces one to change directory before getting a file in that
            directory.

    *   For a Source instance, the same connection should be used for each
        filename that is to be downloaded from the source paths.

        -   This constrains where the final resolution of the filenames should
            be performed.

    To implement (maybe):

    *   What if the parameter is a range?

    *   What if the parameter is given as an open range in the sense that all
        subsequent data, if available, should be downloaded?

    """
    for source in sources:
        log.debug(f"Download source specification: {source.name}")
        match source.protocol:
            case "ftp":
                print("FTP")
                download_ftp(source)
            case "http" | "https":
                print("HTTP")
                download_http(source)
        log.debug("Finished downloading sources")


def is_file(ftp: FTP, candidate: str) -> bool:
    return ftp.nlst(candidate) == [candidate]


def is_directory(ftp: FTP, path: str) -> bool:
    return ftp.nlst(path) != [path]


_FILENAMES: dict[str, str] = {}


def list_files(ftp: FTP, path: str) -> list[str]:
    """
    List files (not sub directories) in given location.

    """
    global _FILENAMES
    if path not in _FILENAMES:
        log.debug(f"Get list of files in FTP directory {path} ...")
        ftp.cwd(path)
        _FILENAMES[path] = [
            candidate for candidate in ftp.nlst() if is_file(ftp, candidate)
        ]
    return _FILENAMES[path]


def download_ftp(source: Source) -> None:
    """
    If filenames is set, assume that the given serverpath is a directory.
    (Or check?)

    If no files names given, make a call to the server and check if the last
    path part is a directory (gets empty list or list of files and
    directories inside the directory.) or a file to be downloaded.

    Cases i can think of, but not necessarily occurring:

    *   What if the filename is parameterised, too?

        -   host/path/to/{year}/filename{doy}.ext
            if host/path/to/{year}/ is resolved first?

        -   So far, it is not.

        -   Since we are using weeks, we need to specify ... ?

    """

    # Log on to the host first, since we need to probe for files directories
    with FTP(source.host) as ftp:
        ftp.login()

        # TODO: Check that we get at least one path
        for pair in source.io_paths:
            # print(pair)
            # print(pair.path_remote, pair.fname)

            # Prepare local

            destination = Path(pair.path_local)
            # Create the destination directory
            destination.mkdir(parents=True, exist_ok=True)

            # Prepare remote

            # Set default remote path
            path_remote = pair.path_remote

            # Check if the URI is a directory or a filename

            # If the filename is a directory to_download is all the files (not
            # directories) inside that directory.

            possible_directory = join(path_remote, pair.fname)
            if not is_file(ftp, possible_directory):
                to_download = list_files(ftp, possible_directory)
                path_remote = possible_directory

            else:
                # TODO: Rewrite this rather long and repeating part to make
                # clear what is going on.

                # Since a given filename may have UNIX-style wildcards in it, we
                # loop over all filenames in the remote path directory and match
                # against the filename pattern in order to only download
                # existing files fromt he server.

                # Get files that match the current source filename
                to_download = [
                    candidate
                    for candidate in list_files(ftp, path_remote)
                    # This, effectively, resolves the actual filename of the file to
                    # download, since fnmatch expands any UNIX-wildcard notation in
                    # the specified filename.
                    if fnmatch(candidate, pair.fname)
                ]

            # Notify if nothing to download
            if not to_download:
                log.info(f"Found no files matching {pair.path_remote}/{pair.fname} ...")
                continue

            # Go to the path
            ftp.cwd(path_remote)

            # Finally, download each of the filenames resolved
            for fname in to_download:
                # Get the resolved destination filename
                ofname = destination / fname

                # TODO: Implement safeguard here, so that we do not always
                # download everything older than a day. Most data should be a
                # one-time thing.
                if already_downloaded(
                    ofname
                ):  # , max_age=pair.max_age):  #  and not force:
                    log.debug(f"{ofname.name} already downloaded ...")
                    continue

                log.info(f"Downloading {ofname.name} ...")
                ftp.retrbinary(f"RETR {fname}", ofname.write_bytes)


_SESSION: requests.Session = None


def get_session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
    return _SESSION


def download_http(source: Source) -> None:
    """
    Download a file over HTTP (TLS or not)

    """
    for pair in source.io_paths:
        destination = Path(pair.path_local)
        destination.mkdir(parents=True, exist_ok=True)
        ofname = destination / pair.fname
        log.info(f"Download {pair.uri} to {ofname} ...")
        r = get_session().get(pair.uri, allow_redirects=True, timeout=30)
        # TODO: Check response is OK, before saving the data
        ofname.write_bytes(r.content)
