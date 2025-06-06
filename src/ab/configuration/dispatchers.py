"""
Dispatch functions are functions that restructure or otherwise pre-process given arguments
to make them work for a specific API-level function used by the TaskDefinition.

"""

from typing import Any

from ab.parameters import ArgumentsType
from ab.paths import resolve_wildcards
from ab.data import compress


def gzip_dispatch(arguments: ArgumentsType) -> list[dict[str, Any]]:
    key = "fname"
    filenames = resolve_wildcards(arguments[key])
    return [{**arguments, **{key: fname}} for fname in filenames]
