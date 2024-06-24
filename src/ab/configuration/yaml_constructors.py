"""
Module for custom PyYAML constructors.

Constructors defined in this module are added to the SafeLoader, which is the
recommended way to load YAML-files.

"""

from pathlib import Path
from typing import Iterable

# import functools

import yaml
from yaml_env_tag import construct_env_tag

from ab.bsw.bpe import BPETask
from ab.data.source import Source
from ab.dates import (
    date_range,
    GPSDate,
)


def resolve_wildcards(path: Path | str) -> Iterable[Path]:
    """
    Return all files resolved by the wildcard.

    If no wild card is given, a single-item list with the given path as a `Path`
    instance is returned.

    """
    path = Path(path)
    # `Path.glob` returns an empty generator, when no wilcard is given.
    if not "*" in str(path):
        # Note that this assumes that no other type of UNIX wildcards such as
        # `[<whatever>]` are used (these are supported by glob).
        return [path]
    parts = path.parts[path.is_absolute() :]
    return Path(path.root).glob(str(Path(*parts)))


def path_constructor(loader: yaml.Loader, node: yaml.Node) -> None | Path | list[Path]:
    """
    The path constructor can work on two types of input:

    1) Fully specified path strings like the following:

    *   scheme://uniform/ressource/identifier
    *   /some/path/to/somewhere
    *   /some/path/to/some.file

    These values will be parsed as YAML ScalarNode instances, and the
    constructor simply returns a Python Path instance of the entire string
    value.

    ---

    2) A sequence of different components useful, when one or more components
       are YAML aliases referring to a string somewhere else in the YAML
       document.

    More complex paths can thus be constructed by supplying the YAML tag with a
    sequence of path elements.

    Here, each sequence item can be either a YAML alias for a value elsewhere in
    the document, or simply a string.

    Examples of the sequence syntax are:

    ```yaml

    key1: [*alias_to_a_base_path, subdirectory, file.txt]
    key2:
    - *alias_to_a_base_path
    - subdirectory
    - file.txt

    ```

    Any element in the sequence, except the first element, may use the common
    wildcard `*` to specify any matching files.

    In this case, the constructor will return not one single Path instance, but
    a list of all matches found, except when only one result is found. In that
    case that single Path instance is returned.

    """
    if not isinstance(node, (yaml.ScalarNode, yaml.SequenceNode)):
        raise KeyError(
            f"Must be single string or list of strings or `Path` instances. Got {node.value!r} ..."
        )

    if isinstance(node, yaml.ScalarNode):
        path: Path = Path(loader.construct_scalar(node))
    else:
        # We use loader.construct_object, since there may be YAML aliases inside.
        # Any YAML alias is assumed to resolve into to a string.
        multiple: list[str | Path] = [loader.construct_object(v) for v in node.value]
        path = Path(*multiple)

    resolved = list(resolve_wildcards(path))

    if not resolved:
        # EnvironmentError(f"Path {path} could not be resolved.")
        return None

    if len(resolved) > 1:
        return resolved

    return resolved[0]


def path_as_str_constructor(loader: yaml.Loader, node: yaml.Node) -> str | list[str]:
    paths = path_constructor(loader, node)
    if isinstance(paths, list):
        return [str(path) for path in paths]
    return str(paths)


def parent_constructor(loader: yaml.Loader, node: yaml.Node) -> Path | str:
    """
    Given a path, the constructor returns the parent directory of that path.

    The constructor can work on fully specified path strings like the following:

    *   /some/path/to/somewhere
    *   /some/path/to/some.file

    In both these cases, a Path instance of the path `/some/path/to` is
    returned.

    The supplied path may be a pointer (YAML alias) to another value in the
    document. In this case, the value must be encapsulated in a YAML sequence:

    *   [*alias]

    If the conversion fails for any reason, the constructor returns an empty
    string.

    """
    # Break if the input is unexpected
    if not isinstance(node, (yaml.ScalarNode, yaml.SequenceNode)):
        raise KeyError(
            f"Must be single string or list of strings. Got {node.value!r} ..."
        )
    # TODO: Remove try-except clauses.
    try:
        if isinstance(node, yaml.ScalarNode):
            # Assume it is a single string specifying a path
            # Grab the string value (a YAML scalar) and make a Path instance
            raw_string_or_path = Path(loader.construct_scalar(node)).absolute().parent

        else:
            # At this point, it is a YAML sequence.
            #
            # We assume that it has a single item which could be a single string
            # or an aliased value.
            #
            # We unpack the single item with `node.value[0]` and construct the
            # object, string or aliased value (presumeably a Path instance or a
            # single string that can be given to the Path constructor).
            raw_string_or_path = loader.construct_object(node.value[0])

        return Path(raw_string_or_path).absolute().parent
    except:
        return ""


def source_constructor(loader: yaml.Loader, node: yaml.MappingNode) -> Source:
    """
    Construct a Source instance from the given keyword arguments.

    """
    return Source(**loader.construct_mapping(node))


def gps_date_constructor(loader: yaml.Loader, node: yaml.ScalarNode) -> GPSDate:
    """
    Convert a YAML timestamp to a GPSDate instance.

    """
    return GPSDate.from_date(loader.construct_yaml_timestamp(node))


def date_to_gps_date_constructor(
    loader: yaml.Loader, node: yaml.SequenceNode
) -> list[GPSDate]:
    """
    Convert a list of Python date or datetime instances (can already be
    `GPSDate` instances as well) to GPSDate instances.

    The constructor assumes that the value of the node is a single-item sequence
    in which the item is the actual object to parse, i.e.

    ```yaml
    key: !Tag [<your content>]
    ```

    This special syntax is chosen, because it allows the user to specify an
    alias to information in another part of the document rather than explicit
    data.

    Putting everything into a sequence will force the parser to replace the
    alias with the corresponding data, before the constructor for the tag is
    invoked.

    The tag constructor then has to pick out the content as the first item of
    the sequence that it was given, in order to have access to the actual data
    inside.

    """
    # Grab aliased or explicitly-written data as the single item in the sequence
    items = loader.construct_sequence(node.value[0])
    return [GPSDate.from_date(date) for date in items]


def date_range_constructor(
    loader: yaml.Loader, node: yaml.MappingNode
) -> list[GPSDate]:
    """
    Construct a list of GPSDate instances based on given beginning and end dates
    (both inclusive).

    """
    d = loader.construct_mapping(node)
    result: list[GPSDate] = date_range(
        d.get("beg"),
        d.get("end"),
        extend_end_by=d.get("extend_end_by", 0),
        transformer=GPSDate,
    )
    return result


def bpe_task_constructor(loader: yaml.Loader, node: yaml.MappingNode) -> BPETask:
    """
    Construct a BPETask instance from the given keyword arguments.

    """
    return BPETask(**loader.construct_mapping(node, deep=True))


yaml.SafeLoader.add_constructor("!ENV", construct_env_tag)
yaml.SafeLoader.add_constructor("!Path", path_constructor)
yaml.SafeLoader.add_constructor("!PathStr", path_as_str_constructor)
yaml.SafeLoader.add_constructor("!Parent", parent_constructor)
yaml.SafeLoader.add_constructor("!Source", source_constructor)
yaml.SafeLoader.add_constructor("!GPSDate", gps_date_constructor)
yaml.SafeLoader.add_constructor("!DateRange", date_range_constructor)
yaml.SafeLoader.add_constructor("!AsGPSDate", date_to_gps_date_constructor)
yaml.SafeLoader.add_constructor("!BPETask", bpe_task_constructor)


# def convert_to_GPSDate_instance(func):
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         return GPSDate.from_date(func(*args, **kwargs))
#     return wrapper


# yaml.SafeLoader.construct_yaml_timestamp = convert_to_GPSDate_instance(yaml.SafeLoader.construct_yaml_timestamp)
