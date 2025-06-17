"""
Transfer and manage local and remote data sources.

"""

from dataclasses import dataclass


@dataclass
class TransferStatus:
    existing: int = 0
    downloaded: int = 0
    failed: int = 0
    not_found: int = 0

    def __add__(self, other) -> "TransferStatus":
        self.existing += other.existing
        self.downloaded += other.downloaded
        self.failed += other.failed
        self.not_found += other.not_found
        return self

    __radd__ = __add__
