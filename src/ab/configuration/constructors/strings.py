"""
String-operation constructor

"""

from typing import (
    Any,
    Final,
)
from collections.abc import Iterable
from dataclasses import (
    dataclass,
    asdict,
)

import yaml

from ab.strings import Operator


METHODS_SUPPORTED: Final = (
    "upper",
    "lower",
    "title",
    "capitalize",
    "lstrip",
    "rstrip",
    "strip",
    "removeprefix",
    "removesuffix",
    "replace",
    "ljust",
    "rjust",
    "swapcase",
    "zfill",
)
"Limit user input by only allowing these string methods"


@dataclass
class OperatorArguments:
    sequence: str
    method: str
    arguments: Iterable[Any] = ()


def string_transform_constructor(loader: yaml.Loader, node: yaml.Node) -> list[str]:
    """
    Configuration example

    ```yaml

    !StringTransform
    sequence: [s1]
    method: upper
    arguments: []

    ```
    """
    if not isinstance(node, yaml.MappingNode):
        raise TypeError(f"Node type {node!r} not supported for tag ...")
    operator_arguments = OperatorArguments(**loader.construct_mapping(node, deep=True))
    sequence, method, arguments = asdict(operator_arguments).values()
    if not all(isinstance(s, str) for s in sequence):
        raise ValueError(f"Sequence items must be strings. Got {sequence!r} ...")
    if not method in METHODS_SUPPORTED:
        raise ValueError(f"Transform method {method!r} not supported ...")
    return [Operator(s).operate(method, *arguments) for s in sequence]
