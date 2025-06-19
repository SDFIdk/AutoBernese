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
