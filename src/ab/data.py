"""
Module for downloading source data

"""
from datetime import date
from ftplib import FTP, FTP_TLS
from pathlib import Path
import logging
from urllib.parse import urlparse

import requests

from ab import configuration

log = logging.getLogger(__name__)


def calc_gps_week(tocalc: date) -> int:
    """Calculates the GPS week number for a given date"""
    gps_epoch = date(1980, 1, 6)  # first GPS week
    return (tocalc - gps_epoch).days // 7


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


def download_sources(*args: list, **kwargs: dict) -> None:
    """
    Download the external files from the specification in the configuration file.
    """
    log.debug("Started downloading sources")
    config = configuration.load()
    i = 0
    for location in config["sources"]:
        log.debug("Downloading " + str(location["name"]))
        parsedurl = urlparse(config["sources"][i]["url"])
        # dest = Path(config["sources"][i]["destination"])
        match parsedurl.scheme:
            case "http" | "https":
                pass
                # download_http(parsedurl.netloc, Path(parsedurl.path), localpath=dest)
            case "ftp" | "ftps":
                pass
                # download_ftp(
                #     parsedurl.scheme,
                #     parsedurl.netloc,
                #     Path(parsedurl.path),
                #     localpath=dest,
                # )
        i += 1
    log.debug("Finished downloading sources")
