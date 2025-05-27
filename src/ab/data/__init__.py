"""
Module for downloading and managing remote data sources.

"""

from dataclasses import dataclass


@dataclass
class DownloadStatus:
    existing: int = 0
    downloaded: int = 0
    failed: int = 0
    not_found: int = 0

    def __add__(self, other) -> "DownloadStatus":
        self.existing += other.existing
        self.downloaded += other.downloaded
        self.failed += other.failed
        self.not_found += other.not_found
        return self

    __radd__ = __add__


# class Handler:
#     def __init__(self, source: Source):
#         self.source = source

#     def __enter__(self):
#         return self.agent

#     def __exit__(self, *args):
#         self.agent.close()


# class Agent:
#     ...
