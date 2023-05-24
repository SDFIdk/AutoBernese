"""
Module for downloading files over FTP.

"""
import datetime as dt
from os.path import join
from pathlib import Path
from ftplib import FTP
from urllib.parse import ParseResult
from fnmatch import fnmatch
from ftplib import (
    FTP,
    error_perm,
)
from typing import (
    Any,
    Iterable,
)
import logging

from ab import configuration
from ab.cache import KeyValueCache
from ab.data.source import Source
from ab.data.stats import already_updated


log = logging.getLogger(__name__)


def is_file(ftp: FTP, candidate: str) -> bool:
    if "*" in candidate:
        return True
    return ftp.nlst(candidate) == [candidate]


def is_directory(ftp: FTP, candidate: str) -> bool:
    if "*" in candidate:
        return False
    return ftp.nlst(candidate) != [candidate]


ifname_directory_listings = (
    configuration.load().get("runtime").get("ftp_directory_listings")
)
_FILENAMES = KeyValueCache(ifname_directory_listings)


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


def download(source: Source) -> None:
    """
    Download paths resolved from a Source instance.

    Two cases are handled:

    *   When the last part of the remote path is a directory, all files
        directory under that directory are downloaded.

    *   When the last part of the remote path is a file, the name is matched
        against the list of files inside the remote parent directory.

        The reason for this is that filenames can use wildcards (such as `*`)
        compatible with Python's `fnmatch`. Hence, each file in the remote
        directory must matched against the given pattern if it is downloaded.

    """

    # Log on to the host first, since we need to probe for files directories
    with FTP(source.host) as ftp:
        ftp.login()

        try:
            for pair in source.resolve():
                # Prepare local destination

                destination = Path(pair.path_local)
                # Create the destination directory
                destination.mkdir(parents=True, exist_ok=True)

                # Prepare remote path

                # Check if given URI is a directory or a filename
                # Default is given remote path
                path_remote = pair.path_remote
                path_remote_candidate = join(path_remote, pair.fname)
                if is_directory(ftp, path_remote_candidate):
                    # Change the remote path, and ...
                    path_remote = path_remote_candidate
                    # when the source URI is a directory, download all files
                    # (excluding directories) inside that directory.
                    to_download = list_files(ftp, path_remote_candidate)

                else:
                    # Get files that match the current source filename
                    to_download = [
                        candidate
                        for candidate in list_files(ftp, path_remote)
                        # This, effectively, resolves the actual filename of the
                        # remote file to download, since the wildcard notation in
                        # the filename specified in the source instance is expanded
                        # using `fnmatch`.
                        if fnmatch(candidate, pair.fname)
                    ]

                # Notify if nothing to download
                if not to_download:
                    log.info(
                        f"Found no files matching {pair.path_remote}/{pair.fname} ..."
                    )
                    continue

                # Go to the path
                ftp.cwd(path_remote)

                # Finally, download each of the filenames resolved
                for fname in to_download:
                    # Get the resolved destination filename
                    ofname = destination / fname

                    if already_updated(ofname, max_age=source.max_age):
                        log.debug(f"{ofname.name} already downloaded ...")
                        continue

                    log.info(f"Downloading {ofname.name} ...")
                    try:
                        # Note: `pathlib.Path.write_text` is awesome, since it
                        # eliminated the use of the with-statement, but when it
                        # is used as a callback function in `retrbinary`, this
                        # is called for each chunk of data, which means that the
                        # file is overwritten with each new chunk only
                        # preserving the last chunk in the 'downloaded' file.
                        # Hence, we stick with the old way.
                        with open(ofname, "wb") as f:
                            ftp.retrbinary(f"RETR {fname}", f.write)
                    except error_perm as e:
                        log.warn(f"Filename {fname} could not be downloaded ...")
                        log.debug(f"{e}")

        except KeyboardInterrupt:
            log.info(f"Interrupted by user. Closing FTP connection ...")
            raise
