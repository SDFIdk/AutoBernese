"""
Define tasks and run them

"""

from typing import Any
import itertools as it
from functools import partial
from collections.abc import (
    Iterable,
    Callable,
)
from dataclasses import (
    dataclass,
    field,
)

from ab.parameters import (
    ArgumentsType,
    ParametersType,
    resolve,
)


@dataclass
class TaskResult:
    finished: bool = False
    return_value: object | None = None
    exception: Exception | None = None


@dataclass
class Task:
    identifier: str
    function: Callable[[Any], Any] = field(repr=False)
    arguments: ArgumentsType
    result: TaskResult = field(repr=False, default_factory=TaskResult)

    def run(self) -> None:
        return_value = None
        finished = False
        exception: Exception | None = None

        try:
            return_value = self.function(**self.arguments)
            finished = True
        except Exception as e:
            exception = e

        self.result = TaskResult(finished, return_value, exception)


def untouched(permutation: ArgumentsType) -> Iterable[ArgumentsType]:
    return [permutation]


@dataclass
class TaskDefinition:
    """
    Compact specification of chosen API-level function to call though a Task
    instance, and, presumably, with many different arguments---although the key
    `arguments` is optional.

    If `parameters` are specified, the `arguments` mapping is treated as a
    template from which a list of instances of arguments is created with each
    instance having any string-typed values formatted using the same parameter
    permutation.

    If the `dispatch_with` function is set, each permutation of arguments is
    passed to this function which is expected to return an iterable of arguments
    that match the signature of the API-level function. This way, arguments may
    be further processed or, simply, restructured to make them work with the
    API-level function.

    The `tasks` method creates Task instances that that can run the API-level
    function with concrete arguments.

    Conclusion: Arguments defined more compactly, may be used, when resolved by
    any parameters, as the actual input to the API-level function, but they can
    also be used as input for the dispatcher function that builds/makes the the
    arguments fit the signature of the API-level function.

    """

    identifier: str
    description: str
    run: Callable[[Any], Any] = field(repr=False)
    dispatch_with: Callable = field(repr=False, default_factory=lambda: untouched)
    arguments: ArgumentsType = field(default_factory=dict)
    parameters: ParametersType = field(default_factory=dict)
    asynchronous: bool = False

    _tasks: list[Task] | None = field(
        init=False, repr=False, default_factory=lambda: None
    )

    _task_id: it.count = field(
        init=False, repr=False, default_factory=partial(it.count, start=1)
    )

    @property
    def task_id(self) -> str:
        minor = next(self._task_id)
        return f"{self.identifier}.{minor:d}"

    @property
    def tasks(self) -> list[Task]:
        """
        Return Task instances for Task Definition instance.

        These are created once, and can thus be referred to several times.

        """
        if self._tasks is None:
            self._tasks = [
                Task(self.task_id, self.run, arguments)
                for permutation in resolve(self.arguments, self.parameters)
                for arguments in self.dispatch_with(permutation)
            ]
        return self._tasks
