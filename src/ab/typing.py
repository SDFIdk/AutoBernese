"""
Common typing annotation for AutoBernese

"""

from collections import abc


type AnyFunction[T, **P] = abc.Callable[P, T]
