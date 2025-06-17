"""
Dispatch functions are functions that restructure or otherwise pre-process given
arguments to make them work for a specific API-level function used by the
TaskDefinition.

Return type for dispatch function must be an Iterable match signature of
API-level function.

"""

from typing import Any
from collections.abc import Iterable

from ab.parameters import ArgumentsType
from ab.paths import resolve_wildcards
from ab.data import compress


type GZipCompressArgumentType = dict[str, Any]


def gzip_dispatch(arguments: ArgumentsType) -> Iterable[GZipCompressArgumentType]:
    key = "fname"
    filenames = resolve_wildcards(arguments[key])
    return [{**arguments, **{key: fname}} for fname in filenames]
