"""
Configuration tools to build TaskDefinition instances

"""

import typing as t
import sys

from ab.typing import AnyFunction
from ab.configuration import (
    SectionListItemType,
    dispatchers,
)
from ab.tasks import TaskDefinition
from ab.imports import import_function
from ab.data import compress
from ab.bsw import bpe
from ab.data import sftp
from ab.station import sta
from ab import vmf


_MODULE: t.Final = sys.modules[__name__]
"This module"


_SHORTCUTS: dict[str, AnyFunction] = {
    # Use as value for `run` key
    "RunBPE": bpe.run_bpe,
    "Compress": compress.gzip,
    "CompressGlob": compress.gzip_glob,
    "SFTPUpload": sftp.upload,
    "Sitelogs2STAFile": sta.create_sta_file_from_sitelogs,
    "BuildVMF": vmf.build,
    "CheckVMF": vmf.check,
    # Tasks to come:
    # "CopyToSAVEDISK":
    #
    # Use as value for `dispatch_with` key
    "DispatchCompress": dispatchers.gzip_dispatch,
    "DispatchVMF": dispatchers.vmf_dispatch,
}
"Shortcut names for API-level functions or pre-processing functions [dispatchers]."


def get_func(name: str) -> AnyFunction:
    if name in _SHORTCUTS:
        return _SHORTCUTS[name]
    elif name in dir(_MODULE):
        candidate: AnyFunction | None = getattr(_MODULE, name)
        assert callable(candidate)
        return candidate
    elif "." in name:
        return import_function(name)
    else:
        raise NameError(name)


def load(kwargs: SectionListItemType) -> TaskDefinition:

    key = "run"
    if not key in kwargs:
        raise RuntimeError(f"Expected {key!r} to be in task definition ...")
    kwargs = {**kwargs, **{key: get_func(kwargs[key])}}

    key = "dispatch_with"
    if key in kwargs:
        kwargs = {**kwargs, **{key: get_func(kwargs[key])}}

    return TaskDefinition(**kwargs)


def load_all(raw: list[SectionListItemType]) -> list[TaskDefinition]:
    return [load(kwargs) for kwargs in raw]
