"""
Work with strings

"""

from typing import Any


class Operator(str):
    def operate(self: str, method: str, /, *args: list[Any]) -> Any:
        assert hasattr(self, method)
        return getattr(self, method)(*args)
