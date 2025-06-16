from collections.abc import Iterable
from pathlib import Path


def resolve_wildcards(path: Path | str) -> Iterable[Path]:
    """
    Return all files resolved by the wildcard.

    If no wild card is given, a single-item list with the given path as a `Path`
    instance is returned.

    """
    path = Path(path)
    # `Path.glob` returns an empty generator, when no wildcard is given.
    if not "*" in str(path):
        # Note that this assumes that no other type of UNIX wildcards such as
        # `[<whatever>]` are used (these are supported by glob).
        return [path]
    parts = path.parts[path.is_absolute() :]
    return Path(path.root).glob(str(Path(*parts)))
