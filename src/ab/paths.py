"""
Work with path wildcards

"""

from typing import Any
from collections.abc import Iterable
from pathlib import Path


def resolve_wildcards(path: Path | str) -> Iterable[Path]:
    """
    Return all files resolved by the wildcards used, or just the match if the
    path exists.

    """
    path = Path(path)
    parts = path.parts[path.is_absolute() :]
    return Path(path.root).glob(str(Path(*parts)))


def _parts(path: str, *, sep: str = "/") -> list[str]:
    """
    Split path string into parts, ignoring prepended directory separator and
    pre- and post-fixed dot `.`, i.e. `./<whatever>` and `<whatever>/.`

    """
    if path.startswith("./"):
        path = path[2:]
    if path.endswith("/."):
        path = path[:-2]
    return [part for part in path.split(sep) if part.strip()]


def _parents(path: str, *, sep: str = "/") -> list[str]:
    """
    Accummulate a list of parent directories.

    """
    parts = _parts(path)
    parents = [parts[0]]
    for ix, part in enumerate(parts[1:]):
        parents.append(sep.join([parents[ix], part]))
    return parents
