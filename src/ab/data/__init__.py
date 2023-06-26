"""
Module for downloading resolve, download and manage remote data sources.

"""
import json
from dataclasses import (
    dataclass,
    asdict,
)


@dataclass
class DownloadStatus:
    existing: int = 0
    downloaded: int = 0

    def __add__(self, other) -> "DownloadStatus":
        return DownloadStatus(
            self.existing + other.existing,
            self.downloaded + other.downloaded
    )

    __radd__ = __add__

    def asdict(self) -> str:
        return asdict(self)
