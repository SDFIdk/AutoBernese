"""
Module for downloading files over FTP.

"""
from pathlib import Path
from ftplib import FTP
from urllib.parse import ParseResult
from fnmatch import fnmatch
import logging


log = logging.getLogger(__name__)


def download(host: str, ifname: Path, ofname: Path) -> None:
    """
    Handles FTP (insecure) and FTPS downloads using anonymous user.

    """
    with FTP(host) as ftp:
        # ftp.login()
        ftp.cwd(f"{ifname.parent}")
        ftp.retrbinary(f"RETR {ifname.name}", ofname.write_bytes)


def list_files(host: str, path: str) -> list[str]:
    """
    List files in given location.

    """
    log.debug(f"List files in FTP directory {parsed.netloc}{parsed.path} ...")
    with FTP(host) as ftp:
        # ftp.login()
        ftp.cwd(path)
        is_file = lambda candidate: ftp.nlst(candidate) == [candidate]
        return [candidate for candidate in ftp.nlst() if is_file(candidate)]


def is_directory(ftp: FTP, path: str) -> bool:
    if not ftp:  # ?
        return False
    return ftp.nlst(path) != [path]
