"""
Source constructor

"""

import yaml

from ab.data.source import Source


def source_constructor(loader: yaml.Loader, node: yaml.MappingNode) -> Source:
    """
    Construct a Source instance from the given keyword arguments in the mapping.

    """
    if not isinstance(node, yaml.MappingNode):
        raise TypeError(f"Node type {node!r} not supported for tag ...")
    return Source(**loader.construct_mapping(node))  # type: ignore[misc]
