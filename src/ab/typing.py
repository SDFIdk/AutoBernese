"""
Common typing annotation for AutopBernese

"""

import typing as t


P = t.ParamSpec("P")
T = t.TypeVar("T")

type AnyFunction = t.Callable[P, T]
