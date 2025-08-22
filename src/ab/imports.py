from importlib import import_module

from ab.typing import AnyFunction


def import_function(specification: str) -> AnyFunction:
    module_spec, func_name = specification.rsplit(".", 1)
    module = import_module(module_spec)
    return getattr(module, func_name)
