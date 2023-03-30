"""
Configuration

"""
from typing import Any
import pathlib
import os
from dataclasses import dataclass

import yaml
from yaml_env_tag import construct_env_tag

from ab import pkg


_CONFIGURATION: Any = None

yaml.SafeLoader.add_constructor("!ENV", construct_env_tag)


def path_constructor(loader: yaml.Loader, node: yaml.Node) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return pathlib.Path(loader.construct_scalar(node)).absolute()

    if isinstance(node, yaml.SequenceNode):
        elements = [loader.construct_object(v) for v in node.value]
        root = pathlib.Path(elements[0])
        return root.joinpath(*elements[1:])

    raise KeyError(f"Must be single string or list of strings. Got {node.value!r} ...")


yaml.SafeLoader.add_constructor("!Path", path_constructor)


def parent_constructor(loader: yaml.Loader, node: yaml.Node) -> Any:
    try:
        if isinstance(node, yaml.ScalarNode):
            # Assume it is a string and return the scalar_constructor.
            construction = pathlib.Path(loader.construct_scalar(node)).absolute().parent

        else:
            # Assume that node.value[0] is a SequenceNode that can be resolved to a
            # string for pathlib.Path.
            construction = loader.construct_object(node.value[0])

        return pathlib.Path(construction).absolute().parent
    except:
        return ""


yaml.SafeLoader.add_constructor("!Parent", parent_constructor)


def load() -> Any:
    """
    Load built-in configuration file for AutoBernese.

    """
    global _CONFIGURATION

    if _CONFIGURATION is not None:
        return _CONFIGURATION

    ifname = pathlib.Path(pkg.configuration)
    if not ifname.is_file():
        raise LookupError(f"Configuration file {ifname} does not exist ...")

    _CONFIGURATION = yaml.safe_load(ifname.read_text())
    return _CONFIGURATION
