"""
Module for downloading source data

"""

import requests
from ftplib import FTP, FTP_TLS
from pathlib import Path


def download_http(domain: str, remotepath: Path, localpath: Path) -> None:
    """Handles HTTP and HTTPS downloads without credentials.
    Allow following redirects for simplicity."""
    r = requests.get(domain + str(remotepath), allow_redirects=True)
    with open(localpath / remotepath.name, "wb") as file:
        file.write(r.content)


def download_ftp(scheme: str, domain: str, remotepath: Path, localpath: Path) -> None:
    """Handles FTP (insecure) and FTPS downloads using anonymous user."""
    if scheme == "ftps":
        ftp = FTP_TLS(domain)  # connect to host, default port
    else:
        ftp = FTP(domain)
    ftp.login()  # user and pass is anonymous
    ftp.cwd(str(remotepath.parent))  # change into the path's parent
    with open(localpath, "wb") as fp:
        ftp.retrbinary("RETR %s" % remotepath.name, fp.write)
    ftp.quit()


def download_sources() -> None:
    print("Downloading A")
    print("Downloading B")
    print("Downloading C")
    print("Downloading D")
    print("Downloading .")
    print("Downloading .")
    print("Downloading .")
    print("Finished")
