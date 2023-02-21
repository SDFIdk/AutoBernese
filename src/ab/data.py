"""
Module for downloading source data

"""

import requests
from ftplib import FTP, FTP_TLS
from pathlib import Path


def download_http(domain: str, path: str, localpath: str) -> None:
    """Handles HTTP and HTTPS downloads without credentials.
    Allow following redirects for simplicity."""
    r = requests.get(domain + path, allow_redirects=True)
    path = Path(localpath)
    with open(localpath + path.name, "wb") as f:
        f.write(r.content)


def download_ftp(scheme: str, domain: str, remotepath: str, localpath: str) -> None:
    """Handles FTP (insecure) and FTPS downloads using anonymous user."""
    localfilepath = Path(localpath)
    remotefilepath = Path(remotepath)
    if scheme == "ftps":
        ftp = FTP_TLS(domain)  # connect to host, default port
    else:
        ftp = FTP(domain)
    ftp.login()  # user and pass is anonymous
    ftp.cwd(str(remotefilepath.parent))  # change into the path's parent
    with open(localfilepath, "wb") as fp:
        ftp.retrbinary("RETR %s" % remotefilepath.name, fp.write)
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
