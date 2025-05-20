"""
Task constructors

"""

import yaml

from ab.bsw.bpe import BPETaskDefinition


def bpe_task_constructor(
    loader: yaml.Loader, node: yaml.MappingNode
) -> BPETaskDefinition:
    """
    Construct a BPETaskDefinition instance from the given keyword arguments.

    NOTE:

    To keep it short in the configuration, there is a knowing mismatch between
    the two types of objects in AutoBernese and their corresponding YAML tags.

    """
    return BPETaskDefinition(**loader.construct_mapping(node, deep=True))  # type: ignore[misc]


# def tropo_task_constructor(loader: yaml.Loader, node: yaml.MappingNode) -> BPETaskDefinition:
#     """
#     Construct a TaskDefinition instance from the given keyword arguments.

#     """
#     raise NotImplementedError
#     # return BPETaskDefinition(**loader.construct_mapping(node, deep=True))  # type: ignore[misc]


# def remote_upload_task_constructor(loader: yaml.Loader, node: yaml.MappingNode) -> RemoteUploadTaskDefinition:
#     """
#     Construct a TaskDefinition instance from the given keyword arguments.

#     """
#     raise NotImplementedError
#     # return BPETaskDefinition(**loader.construct_mapping(node, deep=True))  # type: ignore[misc]
