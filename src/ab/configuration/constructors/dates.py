"""
Date constructors

"""

import datetime as dt
import functools

import yaml

from ab.dates import (
    date_range,
    dates_to_gps_date,
    GPSDate,
)


def date_to_gps_date_constructor(
    loader: yaml.Loader, node: yaml.SequenceNode | yaml.ScalarNode
) -> list[GPSDate] | GPSDate:
    """
    Convert a single instance or a list of Python date or datetime instances
    (can already be `GPSDate` instances as well) to GPSDate instances.

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

    References:

    *   https://stackoverflow.com/a/53779426

    """
    # We chose to use and thus expect a sequence node to allow us to resolve a
    # YAML alias if given instead of an explicit value. See the reference above.
    #
    # For this purpose, we only expect one item in the container. This item can
    # be either a scalar value or another sequence with several scalar values.
    #
    if not isinstance(node, yaml.SequenceNode):
        raise TypeError(f"Node type {node!r} not supported for tag ...")

    # First, Extract the value from our chosen container for the argument(s) to
    # the constructor.
    sub_node = node.value[0]

    if not isinstance(sub_node, (yaml.ScalarNode, yaml.SequenceNode)):
        raise ValueError(
            f"Input argument must be single date or list of date instances ..."
        )

    # The value can be a list of dates.
    if isinstance(sub_node, yaml.SequenceNode):
        # Resolve and extract the list of dates
        dates = loader.construct_sequence(sub_node)
        # Build a list of GPSDate instances to return
        return [GPSDate.from_date(date) for date in dates]

    # Alternatively, the value can be a single date
    if isinstance(sub_node, yaml.ScalarNode):
        # Resolve the timestamp
        date = loader.construct_yaml_timestamp(sub_node)
        # And build the single instance to return
        return GPSDate.from_date(date)


def date_range_constructor(
    loader: yaml.Loader, node: yaml.MappingNode
) -> list[GPSDate]:
    """
    Construct GPSDate instances based on start and end dates (both inclusive) as
    well as how much to extend end date with, if any.

    """
    if not isinstance(node, yaml.MappingNode):
        raise TypeError(f"Node type {node!r} not supported for tag ...")
    d = loader.construct_mapping(node)
    beg = d.get("beg")
    assert isinstance(
        beg, (dt.date, dt.datetime)
    )  # Remember that this only wors for debug mode.
    end = d.get("end")
    extend_end_by = d.get("extend_end_by", 0)
    return dates_to_gps_date(date_range(beg, end, extend_end_by=extend_end_by))


def timestamp2GPSDate(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return GPSDate.from_date(func(*args, **kwargs))

    return wrapper
