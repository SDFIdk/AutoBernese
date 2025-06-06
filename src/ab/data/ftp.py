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
    Iterator,
)
from contextlib import contextmanager
import functools
import logging

from ab import configuration
from ab.data import DownloadStatus
from ab.data.source import Source
from ab.data.stats import already_updated


log = logging.getLogger(__name__)


@functools.cache
def is_file(ftp: FTP, candidate: str) -> bool:
    return ftp.nlst(candidate) == [candidate]


@contextmanager
def specific_path(ftp: FTP, path: str) -> Iterator[FTP]:
    cwd = ftp.pwd()
    log.debug(f"switch to {path} ...")
    ftp.cwd(path)
    try:
        yield ftp
    finally:
        log.debug(f" -> switch back to {cwd} ...")
        ftp.cwd(cwd)


def list_files(ftp: FTP, path: str, *, ix_column: int = 8) -> list[str]:
    """
    List files without looking for a cached version.

    Note: Not all the servers that we access support the newer MLSD command, so
    we rely on the older NLST command.

    Works for non-Windows FTP-servers, where the directory listing is what you
    get with `ls`.

    """
    with specific_path(ftp, path) as tmp:
        tmp.retrlines("LIST", (lines := []).append)  # type: ignore
        return [line.split()[ix_column] for line in lines if not line.startswith("d")]


def download(source: Source) -> DownloadStatus:
    """
    Download paths resolved from a Source instance.

    Logic:

    *   If the filename does not contain wildcards to match against the remote
        directory listing, simply, download the file.

    *   Otherwise, the filename, which we then know contains wildcards, is
        matched against the list of files inside the remote parent directory to
        get all possible files to download based on the given pattern.

    Note:

    *   The assumption for a RemoteLocalPair instance is that the remote path in
        `path_remote` is a directory in which to find the file denoted `fname`.

        For now, the algorithm does not look inside any directory.

    """
    status = DownloadStatus()

    # Log on to the host first, since we need to probe for files directories
    with FTP(source.host) as ftp:
        ftp.login()

        try:
            for pair in source.resolve():

                # Prepare local destination directory
                destination = Path(pair.path_local)
                destination.mkdir(parents=True, exist_ok=True)

                if "*" not in pair.fname:
                    log.debug(
                        f"Filename {pair.fname!r} has no wildcard and is added to the download list."
                    )
                    # If the filename has no wildcard, just download the file
                    candidates = [pair.fname]

                    # NOTE: At this point, we do not know if the filename in
                    # `candidates` exists on the server.

                else:
                    # Get files that match the current source filename
                    log.debug("Searching for wildcard results")
                    candidates = [
                        candidate
                        for candidate in list_files(ftp, pair.path_remote)
                        # This, effectively, resolves the actual filename of the
                        # remote file to download, since the wildcard notation in
                        # the filename specified in the source instance is expanded
                        # using `fnmatch`.
                        if fnmatch(candidate, pair.fname)
                    ]

                    # NOTE: At this point, we do know that the filenames in
                    # `candidates` actually exist on the server.

                if not candidates:
                    log.info(
                        f"Found no files matching {pair.path_remote}/{pair.fname} ..."
                    )
                    status.not_found += 1
                    continue

                # Filter out files already available
                to_download = []
                for fname in candidates:
                    # Get resolved destination filename
                    ofname = destination / fname
                    if already_updated(ofname, max_age=source.max_age):
                        log.debug(f"{ofname.name} already downloaded ...")
                        status.existing += 1
                        continue
                    to_download.append((fname, ofname))

                # Finally, download each of the filenames resolved
                ftp.cwd(pair.path_remote)
                for fname, ofname in to_download:
                    log.info(f"Downloading {fname} ...")
                    try:
                        # NOTE: `pathlib.Path.write_text` can not be used as a
                        # callback function in `retrbinary`, because it is
                        # called for each chunk of data, which means that the
                        # file is overwritten with each new chunk, thus only
                        # preserving the last chunk in the 'downloaded' file.

                        # Therefore, we use the write on the context manager
                        with open(ofname, "wb") as f:
                            ftp.retrbinary(f"RETR {fname}", f.write)

                    except error_perm as e:
                        log.warn(f"Filename {fname} could not be downloaded ...")
                        log.debug(f"{e}")
                        log.info(f"Deleting empty or incomplete {ofname} ...")
                        ofname.unlink()
                        status.failed += 1
                        continue

                    status.downloaded += 1

        except KeyboardInterrupt:
            log.info(f"Interrupted by user. Closing FTP connection ...")
            raise

    return status
