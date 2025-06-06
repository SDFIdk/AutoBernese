from collections.abc import Callable
from importlib import import_module


def import_function(specification: str) -> Callable:
    module_spec, func_name = specification.rsplit(".", 1)
    module = import_module(module_spec)
    return getattr(module, func_name)
