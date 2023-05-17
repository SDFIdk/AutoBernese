"""
Module for custom PyYAML constructors.

Constructors defined in this module are added to the SafeLoader, which is the
recommended way to load YAML-files.

"""
import datetime as dt
import pathlib

import yaml
from yaml_env_tag import construct_env_tag

from ab.data.source import Source
from ab.dates import (
    date_range,
    GPSDate,
)


def path_constructor(
    loader: yaml.Loader, node: yaml.Node
) -> pathlib.Path | list[pathlib.Path]:
    if isinstance(node, yaml.ScalarNode):
        return pathlib.Path(loader.construct_scalar(node)).absolute()

    if not isinstance(node, yaml.SequenceNode):
        raise KeyError(
            f"Must be single string or list of strings. Got {node.value!r} ..."
        )

    # Let the first item be the root of the specified path
    first, *after = [loader.construct_object(v) for v in node.value]
    root = pathlib.Path(first)  # .resolve()

    # Case: The user is using a wild card to get at one or many files.
    if any("*" in element for element in after):
        # Generate results
        full_paths = [full_path for full_path in root.glob("/".join(after))]

        # Return only the one item
        if len(full_paths) == 1:
            return full_paths[0]

        # Return the entire list of results
        elif len(full_paths) > 1:
            return full_paths

    # Return the specified path
    return root.joinpath(*after)


def parent_constructor(loader: yaml.Loader, node: yaml.Node) -> pathlib.Path | str:
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


def source_constructor(loader: yaml.Loader, node: yaml.MappingNode) -> Source:
    return Source(**loader.construct_mapping(node))


def date_range_constructor(
    loader: yaml.Loader, node: yaml.MappingNode
) -> list[dt.date]:
    d = loader.construct_mapping(node)
    return date_range(d.get("beg"), d.get("end"), transformer=GPSDate)


yaml.SafeLoader.add_constructor("!ENV", construct_env_tag)
yaml.SafeLoader.add_constructor("!Path", path_constructor)
yaml.SafeLoader.add_constructor("!Parent", parent_constructor)
yaml.SafeLoader.add_constructor("!Source", source_constructor)
yaml.SafeLoader.add_constructor("!DateRange", date_range_constructor)
