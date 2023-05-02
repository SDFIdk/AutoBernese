"""
Module for handling an external data source.

"""
from os.path import join
from typing import (
    Any,
    Iterable,
)
import itertools as it
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import (
    urlparse,
    ParseResult,
)
import logging


log = logging.getLogger(__name__)


# Parameter expansion
def resolved(parameters: dict[str, tuple[Any]]) -> dict[str, Any]:
    inverted = {tuple(values): key for (key, values) in parameters.items()}
    return [
        {key: value for (key, value) in zip(parameters.keys(), values)}
        for values in it.product(*inverted.keys())
    ]


def resolvable(
    parameters: dict[str, Iterable[Any]], string_to_format: str
) -> dict[str, Iterable[Any]]:
    """
    Return dict with parameters that are actually employed in formatabale.

    This function exists, because the user may provide more parameters than are
    usable, and the mechanism that expands the dict of parameters and possible
    values to a list of dicts with each possible combination of parameter value
    will provide duplicate file listings when the name is resolved for each
    parameter combination where the difference in parameter value is only in the
    not-used parameter (which is ignored by the .format() method).

    """
    return {
        parameter: values
        for (parameter, values) in parameters.items()
        # Case: 'Whatever comes before {parameter} whatever comes after'
        if f"{{{parameter}}}" in string_to_format
        # Case: 'Whatever comes before {parameter.property} whatever comes after'
        or f"{{{parameter}." in string_to_format
    }


@dataclass
class RemoteLocalPair:
    uri: str
    path_local: str

    def __post_init__(self) -> None:
        # Remote
        _parsed: ParseResult = urlparse(self.uri)

        # self.protocol: str = _parsed.scheme
        # self.host: str = _parsed.netloc

        # TODO: Check assumption
        # Assumption: the URI is a path to a file
        path = Path(_parsed.path)
        self.path_remote: str = str(path.parent)
        self.fname: str = str(path.name)

        # Local path
        #
        # A local path will not work, if the destination filename is a wildcard.
        # Better to let the download tool resolve the final filename.


@dataclass
class Source:
    """
    A source object with one path (pattern) and specific or all files to get.

    Filenames are resolved offline and can be used to match against the source
    path, when connected to the remote server.

    """

    name: str
    url: str | Path
    destination: str | Path
    filenames: list[str | Path] = None
    parameters: dict[str, Iterable[Any]] = None

    """
    Steps:

    *   Parse url, to get the path isolated
    *   Resolve path combinations
    *   Resolve filenames (hard)

    """

    def __post_init__(self):
        # Path version for path joining
        self.destination = Path(self.destination)

        # String version for formatting
        self.destination_ = str(self.destination)

        # Have each component
        self._parsed: ParseResult = urlparse(self.url)
        self.protocol: str = self._parsed.scheme
        self.host: str = self._parsed.netloc

    @property
    def io_paths(self) -> list[tuple[str]]:
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
