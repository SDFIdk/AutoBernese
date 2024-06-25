"""
Module for protocols.

"""

from typing import Protocol


class TaskRunner(Protocol):
    """Protocol type for a task runner."""

    def run(self) -> None:
        """Run task"""


class Task(Protocol):
    """Protocol type for a task."""

    def runners(self) -> list[TaskRunner]:
        """Return list of TaskRunner instances"""
