"""
Module for downloading source data

"""
import os
import requests
from ftplib import FTP, FTP_TLS


def download_http(domain: str, path: str, localpath: str) -> None:
    """Handles HTTP and HTTPS downloads without credentials.
    Allow following redirects for simplicity."""
    r = requests.get(domain + path, allow_redirects=True)
    open(localpath + os.path.basename(path), "wb").write(r.content)


def download_ftp(scheme: str, domain: str, path: str, localpath: str) -> None:
    """Handles FTP (insecure) and FTPS downloads.
    FTP should NOT be used except with 'anonymous' as username and password."""
    if scheme == "ftps":
        ftp = FTP_TLS(domain)  # connect to host, default port
    else:
        ftp = FTP(domain)
    ftp.login()  # user and pass is anonymous
    ftp.cwd(os.path.dirname(path))  # change into the specified directory
    with open(localpath + os.path.basename(path), "wb") as fp:
        ftp.retrbinary("RETR %s" % os.path.basename(path), fp.write)
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
