"""
Common command-output

"""

import os
from typing import Final
from collections.abc import Iterable
import logging

from rich import print

from ab.tasks import Task


log = logging.getLogger(__name__)

TERM_WIDTH: Final = os.get_terminal_size().columns


def divide(fill: str = "=", /) -> str:
    assert isinstance(fill, str)
    assert len(fill) == 1
    return fill * TERM_WIDTH


def title_divide(s: str, fill: str = "=", /, *, pad: int = 1) -> str:
    assert isinstance(fill, str)
    assert len(fill) == 1
    padding = " " * pad
    return f"{padding}{s.title()}{padding}".center(TERM_WIDTH, fill)


def print_task_result_and_exception(tasks: Iterable[Task]) -> None:
    print(title_divide("Task execution status"))
    for task in tasks:
        result = task.result

        if result.finished and result.exception is None:
            log.info(
                f"{task.identifier} finished and returned {result.return_value!r} ..."
            )
            postfix = "[green][ done ][/]"
        else:
            log.info(
                f"{task.identifier} failed with exception ({result.exception}) ..."
            )
            postfix = "[red][ error ][/]"

        # A single line for the task ID and overall status
        print(title_divide("Task", "-"))
        print(f"{task.identifier}: {postfix}")

        # The result if this is returned from the function called by run
        if result.return_value:
            print(title_divide("Return value", "."))
            print(result.return_value)
            # print(divide("-"))

        # Captured exception
        if result.exception:
            print(title_divide("Exception", "."))
            print(result.exception)

    print(divide())
    print()
