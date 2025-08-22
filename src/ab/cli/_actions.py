"""
Common command actions

"""

import asyncio
from collections.abc import (
    Callable,
    Iterable,
)

from rich import print

from ab.cli import _output
from ab.tasks import Task


def run_tasks(tasks: Iterable[Task]) -> None:
    """
    Run tasks, synchronously

    """
    for task in tasks:
        task.run()


def run_tasks_async(tasks: Iterable[Task]) -> None:
    """
    Run tasks, asynchronously

    """

    async def resolved_tasks() -> None:
        async_tasks = [asyncio.to_thread(task.run) for task in tasks]
        await asyncio.gather(*async_tasks)

    asyncio.run(resolved_tasks())


def get_task_runner(asynchronous: bool) -> Callable[[list[Task]], None]:
    if asynchronous is True:
        return run_tasks_async
    return run_tasks
