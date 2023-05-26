"""
Module for running the Bernese Processing Engine [BPE]

"""
from typing import (
    Any,
    Mapping,
    Iterable,
    Final,
    Protocol,
)
import os
import logging
import subprocess as sub
from dataclasses import (
    dataclass,
    asdict,
)

from ab import pkg
from ab.parameters import (
    resolvable,
    resolved,
)


log = logging.getLogger(__name__)


class Task(Protocol):
    """Protocol type for a task."""

    def run(self) -> None:
        """Run task"""


@dataclass
class BPEInput:
    """
    When run, the task instance will be updated with the actual details of the
    session.

    """

    pcf_file: str
    campaign: str
    year: str
    session: str
    sysout: str
    status: str
    taskid: str
    cpu_file: str = "USER"

    def resolve(self, parameters: dict[str, Iterable[Any]]) -> list[dict[str, str]]:
        """
        TODO: Clarify
        Resolve parameters given into possible BPE input used.

        For each possible parameter value each instance variable is formatted.

        Returns a list of dictionaries with the class members as keys and their formatted values as each key's values.

        """
        templates = asdict(self)
        return [
            {
                name: template.format(**resolvable(combination, template))
                for (name, template) in templates.items()
            }
            for combination in resolved(parameters)
        ]


@dataclass
class BPETask:
    """ """

    name: str
    spec: BPEInput = "foo"
    parameters: dict[str, Iterable[Any]] = None

    def __post_init__(self) -> None:
        self.spec = BPEInput(**self.spec)

    def run(self) -> None:
        for bpe_metadata in self.spec.resolve(self.parameters):
            # print(bpe_metadata)
            run(as_environment_variables(**bpe_metadata))
            break


KEYS_BPE: set[str] = {
    "AB_BPE_PCF_FILE",
    "AB_BPE_CPU_FILE",
    "AB_BPE_CAMPAIGN",
    "AB_BPE_YEAR",
    "AB_BPE_SESSION",
    "AB_BPE_SYSOUT",
    "AB_BPE_STATUS",
    "AB_BPE_TASKID",
}

_PREFIX: Final[str] = "AB_BPE_"


def as_environment_variables(**parameters: dict[str, str]) -> dict[str, str]:
    if not all(isinstance(key, str) for key in parameters):
        raise TypeError("Keys must be of type `str` ...")
    if not all(key.replace(" ", "") == key for key in parameters):
        raise ValueError("Keys may not contain spaces ...")
    return {f"{_PREFIX}{key.upper()}": value for (key, value) in parameters.items()}


def run(bpe_env: Mapping = None) -> None:
    """
    Start specified Proces Control File with Bernese Processing Engine [BPE].

    Technically, Python runs Perl-program that initiates and starts BPE with
    given PCF.

    Parameters: {', '.join(SETTINGS_DEFAULT_BPE.keys())}

    """
    if not bpe_env:
        log.debug("Use default BPE settings ...")

    keys_gotten = set(bpe_env)
    diff = KEYS_BPE - keys_gotten
    if diff:
        msg = "PCF metadata missing {diff!r}"
        log.error(msg)
        raise ValueError(msg)

    log.info(f"Using the following PCF metadata as input:")
    sz = max(len(key) for key in bpe_env)
    for key, value in bpe_env.items():
        log.info(f"{key: <{sz}s}: {value}")
    try:
        log.debug(f"Run BPE runner ...")
        process = sub.Popen(f"{pkg.bpe_runner}", env={**os.environ, **bpe_env})
        process.wait()
        log.debug(f"BPE runner finished ...")

    except KeyboardInterrupt:
        log.debug(f"BPE runner killed ...")

    finally:
        process.terminate()
        process.kill()
