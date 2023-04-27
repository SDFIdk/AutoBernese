"""
Module for downloading files over FTP.

"""
from pathlib import Path
from ftplib import FTP
from urllib.parse import ParseResult
import logging


log = logging.getLogger(__name__)


# _SESSIONS: dict[str, FTP] = {}


# def get_session(domain: str) -> FTP:
#     global _SESSIONS
#     if domain not in _SESSIONS:
#         _SESSIONS[domain] = FTP(domain)


def download(
    domain: str, remotepath: Path, ofname: Path
) -> None:
    """
    Handles FTP (insecure) and FTPS downloads using anonymous user.

    """
    with FTP(domain) as ftp:
        ftp.login()
        ftp.cwd(f"{remotepath.parent}")
        ftp.retrbinary(f"RETR {remotepath.name}", ofname.write_bytes)


def list_files(parsed: ParseResult) -> list[str]:
    """
    List files in given location.

    """
    log.debug(f"List files in FTP directory {parsed.netloc}{parsed.path} ...")
    with FTP(parsed.netloc) as ftp:
        ftp.login()
        ftp.cwd(parsed.path)
        is_file = lambda candidate: ftp.nlst(candidate) == [candidate]
        return [candidate for candidate in ftp.nlst() if is_file(candidate)]
