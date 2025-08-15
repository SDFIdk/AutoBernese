"""
Common typing annotation for AutopBernese

"""

from collections.abc import Callable
from typing import (
    Any,
    TypeVar,
)


DecoratedFunction = TypeVar("DecoratedFunction", bound=Callable[..., Any])
"Match any function, when creating a decorator"
