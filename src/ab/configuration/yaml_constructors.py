"""
Module for custom PyYAML constructors.

Constructors defined in this module are added to the SafeLoader, which is the
recommended way to load YAML-files.

"""

import datetime as dt
from pathlib import Path
from typing import Iterable
import functools

import yaml
from yaml_env_tag import construct_env_tag  # type: ignore

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


def path_constructor(loader: yaml.Loader, node: yaml.Node) -> Path | list[Path]:
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

    2) A sequence of path components, which is useful when one or more
       components are YAML aliases referring to a string somewhere else in the
       YAML document.

    More complex paths can thus be constructed by supplying the YAML tag with a
    sequence of path elements.

    Here, each sequence item can be either a YAML alias for a value elsewhere in
    the document, or simply a string.

    Examples of the sequence syntax are:

    ```yaml

    key1: !Path [*alias_to_a_base_path, subdirectory, file.txt]

    ```

    Return types
    ------------

    Any element in the path or sequence of path components (except the first
    element), may use the common wildcard `*` to specify any matching files.

    In this case, the constructor will return not one single Path instance, but
    a list of all matches found, except when only one result is found. In that
    case that single Path instance is returned.

    """
    if not isinstance(node, (yaml.ScalarNode, yaml.SequenceNode)):
        raise KeyError(
            f"Must be single string or list of strings or `Path` instances. Got {node.value!r} ..."
        )

    if isinstance(node, yaml.ScalarNode):
        raw = loader.construct_scalar(node)
        if not isinstance(raw, str):
            raise RuntimeError(f"Expected {raw!r} to be a string.")
        path: Path = Path(raw)
    else:
        # We use loader.construct_object, since there may be YAML aliases inside.
        multiple: list[str | Path] = [loader.construct_object(v) for v in node.value]
        path = Path(*multiple)

    # Avoid relative paths `dir/../dir2`
    path = path.absolute()

    resolved = list(resolve_wildcards(path))

    if not resolved:
        EnvironmentError(f"Path {path!r} could not be resolved.")

    if len(resolved) > 1:
        return resolved

    return resolved[0]


def path_as_str_constructor(loader: yaml.Loader, node: yaml.Node) -> str | list[str]:
    paths = path_constructor(loader, node)
    if isinstance(paths, list):
        return [str(path) for path in paths]
    return str(paths)


def parent_constructor(loader: yaml.Loader, node: yaml.Node) -> Path | list[Path]:
    """
    Returns the parent directory of the path given.

    Expected input is the same as for path_contructor.

    """
    paths = path_constructor(loader, node)
    if isinstance(paths, list):
        return [path.parent for path in paths]
    return paths.parent


def source_constructor(loader: yaml.Loader, node: yaml.MappingNode) -> Source:
    """
    Construct a Source instance from the given keyword arguments.

    """
    return Source(**loader.construct_mapping(node))  # type: ignore[misc]


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

    beg = d.get("beg")
    if not isinstance(beg, (dt.datetime, dt.date)):
        raise TypeError(f"Expected {beg!r} to be a date or datetime instance ...")

    end = d.get("end")
    if not isinstance(end, (dt.datetime, dt.date)):
        raise TypeError(f"Expected {end!r} to be a date or datetime instance ...")

    extend_end_by = d.get("extend_end_by", 0)
    if not isinstance(extend_end_by, int):
        raise TypeError(f"Expected {extend_end_by!r} to be an integer ...")

    return list(
        date_range(beg, end, transformer=GPSDate, extend_end_by=extend_end_by)  # type: ignore
    )


def date_offset_constructor(loader: yaml.Loader, node: yaml.MappingNode) -> GPSDate:
    """
    Using input date and number of days to offset, return the offset date.

    """
    d = loader.construct_mapping(node)

    date = d.get("date")
    if not isinstance(date, (dt.datetime, dt.date)):
        raise TypeError(f"Expected {date!r} to be a date or datetime instance ...")

    days = d.get("days")
    if not isinstance(days, int):
        raise TypeError(f"Expected {days!r} to be an integer ...")

    return GPSDate.from_date(date) + dt.timedelta(days=days)


# def middle_epoch_constructor(
#     loader: yaml.Loader, node: yaml.MappingNode
# ) -> GPSDate:
#     """
#     From given beginning and end dates, return the middle date.

#     If the list of dates has even number of dates, choose the left, except if
#     the argument use_right is True.

#     """
#     dates = date_range_constructor(loader, node)
#     # Get the raw input data anyway, to extract constructor-specific arguments.
#     d = loader.construct_mapping(node)
#     if d.get("right", False) == True:
#         return len(dates) // 2 + 1
#     return len(dates) // 2
#     #  0  1 [2] 3  4
#     # [1, 2, 3, 4, 5]  :: len // 2 == 5 // 2 == 2 :: so index 2 is selected, i.e. the middle.

#     #  0  1  2,[3] 4  5
#     # [1, 2, 3, 4, 5, 6]  :: len // 2 == 6 // 2 == 3 :: So index 2 is selected, i.e. the middle.


def bpe_task_constructor(loader: yaml.Loader, node: yaml.MappingNode) -> BPETask:
    """
    Construct a BPETask instance from the given keyword arguments.

    """
    return BPETask(**loader.construct_mapping(node, deep=True))  # type: ignore[misc]


def convert_to_GPSDate_instance(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("Called the wrapper ...")
        return GPSDate.from_date(func(*args, **kwargs))

    return wrapper


def init():
    yaml.SafeLoader.add_constructor("!ENV", construct_env_tag)
    yaml.SafeLoader.add_constructor("!Path", path_constructor)
    yaml.SafeLoader.add_constructor("!PathStr", path_as_str_constructor)
    yaml.SafeLoader.add_constructor("!Parent", parent_constructor)
    yaml.SafeLoader.add_constructor("!Source", source_constructor)
    yaml.SafeLoader.add_constructor("!GPSDate", gps_date_constructor)
    yaml.SafeLoader.add_constructor("!DateRange", date_range_constructor)
    yaml.SafeLoader.add_constructor("!AsGPSDate", date_to_gps_date_constructor)
    yaml.SafeLoader.add_constructor("!DateOffset", date_offset_constructor)
    yaml.SafeLoader.add_constructor("!BPETask", bpe_task_constructor)

    # Update the constructor for timestamps, so that it makes timestamps GPSDate
    # instances.

    # TODO or not TODO (all timestamps will be converted)
    # from yaml.loader import SafeLoader
    # tag = "tag:yaml.org,2002:timestamp"
    # func = SafeLoader.yaml_constructors[tag]
    # SafeLoader.yaml_constructors[tag] = convert_to_GPSDate_instance(func)
