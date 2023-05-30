"""
Module for protocols.

"""
from typing import Protocol


class Task(Protocol):
    """Protocol type for a task."""

    def run(self) -> None:
        """Run task"""
