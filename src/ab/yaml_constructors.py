"""
Module for custom PyYAML constructors.

Constructors defined in this module are added to the SafeLoader, which is the
recommended way to load YAML-files.

"""
import pathlib
from typing import Any

import yaml
from yaml_env_tag import construct_env_tag


def path_constructor(loader: yaml.Loader, node: yaml.Node) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return pathlib.Path(loader.construct_scalar(node)).absolute()

    if isinstance(node, yaml.SequenceNode):
        first, *after = [loader.construct_object(v) for v in node.value]
        root = pathlib.Path(first)
        if any('*' in element for element in after):
            full_paths = [full_path for full_path in root.glob('/'.join(after))]
            if full_paths:
                return full_paths[0]
        return root.joinpath(*after)

    raise KeyError(f"Must be single string or list of strings. Got {node.value!r} ...")


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


yaml.SafeLoader.add_constructor("!ENV", construct_env_tag)
yaml.SafeLoader.add_constructor("!Path", path_constructor)
yaml.SafeLoader.add_constructor("!Parent", parent_constructor)
