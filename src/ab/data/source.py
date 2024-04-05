"""
Module for handling an external data source.

"""
from os.path import join
from typing import (
    Any,
    Iterable,
)
from dataclasses import dataclass
import math
from pathlib import Path
from urllib.parse import (
    urlparse,
    ParseResult,
)
import logging

from ab.parameters import (
    resolvable,
    resolved,
)

log = logging.getLogger(__name__)


@dataclass
class RemoteLocalPair:
    """
    This is a class for transferring a remote filepath and local destination
    directory path with some additional values being derived from the initial
    input to make it easier to handle for a function that makes the actual
    transfer of data from the remote souce and the local destination.

    """

    uri: str
    path_local: str

    def __post_init__(self) -> None:
        # Assumption: the URI is a path to a file

        # Code annotated with an example:
        # Given: uri = 'https://example.com/filename.txt'
        parsed = urlparse(self.uri)
        # Then: `parsed.path` will be the full path (without protocol) to
        # `filename.txt`
        filepath = Path(parsed.path)
        # Then filepath is a Path instance, from which we can get the remote
        # directory path and the filename of the file to download.
        self.path_remote: str = str(filepath.parent)
        self.fname: str = str(filepath.name)


@dataclass
class Source:
    """
    A source object with one path (pattern) and specific or all files to get.

    Filenames are resolved offline and can be used to match against the source
    path, when connected to the remote server.

    Steps:

    *   Parse url, to get the path isolated
    *   Resolve path combinations
    *   Resolve filenames (hard)

    A source is a source and not a downloader. The source can yield a list of
    files to download if any filenames are specified.

    A Source instance can tell what method (scheme in URL language) is used so
    that the user can use the right tool to get the source.

    Source may not be the best name, since it contains information about the
    corresponding file destination(s).

    A Source instance handles the following input:

    *   The destination is always assumed to be a directory in which to store
        the downloaded files given their resolved paths.

        -   Given a source file, the destination directory is also seen as
            completely specified in that the file is simply put into the
            destination directory.

    *   If the source URL points to a directory, all files (no sub directories)
        within this directory are downloaded to the destination directory. The
        destination directory may have a different name.

        -   The sign that the entire FTP directory should be downloaded is that
            there are no specific filenames given.

    *   Given a source with a dictionary of parameters, a list of dictionaries
        with each parameter-combination (one value for each parameter) is
        generated, and the source may thereby have many paths for the server.

        -   If filenames are given, they are added to each resolved path.

    *   Any filenames specified are resolved in the following manner:

        -   If there are more paths given a set of parameters, the specified
            source files are downloaded for each of the paths resolved.

        -   Filenames may contain UNIX wildcard patterns as can be matched
            against using Python's fnmatch module. (See what wildards are
            matchable in the documentation for fnmatch.)

    Questions addressed:

    *   Where to add the final URL parsing that will give the host/domain, path
        to download from?

    *   How to best return an interable of the remote and local filepaths to the
        user?

        -   For HTTP, this is easy, since the paths can be completely specified
            from the beginning, as they should be known in advance, since there
            is no way of listing a directory for the one HTTP source we have so
            far.

            For HTTP, there is no need to split the URL up into smaller parts
            (host, path, filename).

        -   For FTP, the need for downloading data using wildcard characters,
            means that the filenames must come from an active connection to the
            FTP-server so that the directory listing can be obtained, and, here,
            the filenames are used without their full path, since the protocol
            forces one to change directory before getting a file in that
            directory. TODO: Rewrite and/or move to RemoteLocalPair __doc__

    *   For a given Source instance, the same connection should be used for each
        filename that is to be downloaded from the source paths.

        -   This constrains where the final resolution of the filenames should
            be performed.

    *   What if the parameter is a range?

        -   So far, a range of dates can be made from the configuration file
            using the `!DateRange` YAML tag and a mapping with `beg` and `end`
            being the beginning and end dates (both will be included).

    To implement (maybe):

    *   What if the parameter is given as an open range in the sense that all
        subsequent data, if available, should be downloaded?

    """

    identifier: str
    description: str
    url: str | Path
    destination: str | Path
    filenames: list[str | Path] = None
    parameters: dict[str, Iterable[Any]] = None
    max_age: int | float = math.inf

    def __post_init__(self):
        # Path version for path joining
        self.destination = Path(self.destination)

        # String version for formatting
        self.destination_ = str(self.destination)

        # Have each component
        self._parsed: ParseResult = urlparse(self.url)
        self.protocol: str = self._parsed.scheme
        self.host: str = self._parsed.netloc

    def resolve(self) -> list[RemoteLocalPair]:
        """
        Return all combinations of URL + filename (if any of the latter).

        *   URIs are obtained for each filename, if given.
        *   Each URI is then expanded so that all parameter combinations are used.

        """
        if self.filenames:
            # Example: ftp://example.com/subdir/{year}/
            #           with filenames: ['filename_*.txt', 'othername_{year}.foo']
            urls = [join(self.url, filename) for filename in self.filenames]
        else:
            # Example: https://example.com/filename.txt
            # Example: ftp://example.com/filename.txt
            # Example: ftp://example.com/subdir/{pattern}/filename{numbers}.txt ,
            #           given parameters {'pattern': ['a', 'b'], 'numbers': [1, 2]}
            urls = [self.url]

        if self.parameters is None:
            return [RemoteLocalPair(url, self.destination_) for url in urls]

        return [
            RemoteLocalPair(
                url.format(**combination), self.destination_.format(**combination)
            )
            for url in urls
            for combination in resolved(resolvable(self.parameters, url))
        ]
