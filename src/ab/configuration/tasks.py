"""
Configuration tools to build TaskDefinition instances

"""

from typing import (
    Any,
    Final,
)
from collections.abc import (
    Callable,
    Iterable,
)
import sys

from ab.tasks import (
    TaskDefinition,
    ArgumentsType,
)
from ab.imports import import_function
from ab.data import compress
from ab.bsw import bpe
from ab.data import sftp
from ab.station import sta
from ab import vmf


_MODULE: Final = sys.modules[__name__]
"This module"

_SHORTCUTS: dict[str, Callable] = {
    "RunBPE": bpe.run_bpe,
    "Compress": compress.gzip,
    "SFTPUpload": sftp.upload,
    # Tasks to come
    # "Sitelogs2STAFile": sta.create_sta_file_from_sitelogs,
    # "BuildTroposphereGrdFiles": vmf.nonexisting_builder,
}
"Shortcut names for API-level functions or pre-processing functions."


def get_func(name: str) -> Callable:
    if name in _SHORTCUTS:
        return _SHORTCUTS[name]
    elif name in dir(_MODULE):
        return getattr(_MODULE, name)
    elif "." in name:
        return import_function(name)
    else:
        raise NameError(name)


def load(kwargs: ArgumentsType) -> TaskDefinition:

    key = "run"
    if not key in kwargs:
        raise RuntimeError(f"Expected {key!r} to be in task definition ...")
    kwargs = {**kwargs, **{key: get_func(kwargs[key])}}

    key = "dispatch_with"
    if key in kwargs:
        kwargs = {**kwargs, **{key: get_func(kwargs[key])}}

    return TaskDefinition(**kwargs)


def load_all(raw: list[ArgumentsType]) -> list[TaskDefinition]:
    return [load(kwargs) for kwargs in raw]
