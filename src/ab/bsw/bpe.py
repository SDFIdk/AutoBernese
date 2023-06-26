"""
Module for running the Bernese Processing Engine [BPE]

"""
from typing import (
    Any,
    Mapping,
    Iterable,
    Final,
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


@dataclass
class BPETaskArguments:
    """
    BPE task arguments contains the input needed for running a BPE task.

    The members can be used as is, e.g.

    ```
    instance = BPETaskArguments(...)
    run_bpe(as_environment_variables(asdict(instance)))
    ```

    Alternatively, each member can be a template string that can be resolved using the
    method `resolve` and given a dictionary of parameters that fit the template.

    """

    pcf_file: str
    campaign: str
    year: str
    session: str
    sysout: str
    status: str
    taskid: str
    cpu_file: str = "USER"

    def resolve(
        self, parameters: dict[str, Iterable[Any]] | None
    ) -> list[dict[str, str]]:
        """
        Returns a list of dictionaries with the class members as keys and their
        formatted values as each key's values.

        Create every possible expansion of any template strings in the
        instance's members using the given parameters.

        """
        if parameters is None:
            return []
        instance_members = asdict(self)
        return [
            {
                member: value.format(**resolvable(combination, value))
                for (member, value) in instance_members.items()
            }
            for combination in resolved(parameters)
        ]


@dataclass
class BPETask:
    """ """

    name: str
    arguments: dict[str, Any]
    parameters: dict[str, Iterable[Any]] | None = None

    def __post_init__(self) -> None:
        self._arguments: BPETaskArguments = BPETaskArguments(**self.arguments)

    def run(self) -> None:
        for arguments_resolved in self._arguments.resolve(self.parameters):
            run_bpe(as_environment_variables(arguments_resolved))


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
"Needed BPE environment variables for the AutoBernese BPE runner"

_PREFIX: Final[str] = "AB_BPE_"


def as_environment_variables(parameters: dict[str, str]) -> dict[str, str]:
    """
    Return a dictionary with upper-case keys prefixed to avoid name clash.
    Values remain unchanged.

    """
    if not all(isinstance(key, str) for key in parameters):
        raise TypeError("Keys must be of type `str` ...")
    if not all(key.replace(" ", "") == key for key in parameters):
        raise ValueError("Keys may not contain spaces ...")
    return {f"{_PREFIX}{key.upper()}": value for (key, value) in parameters.items()}


def run_bpe(bpe_env: Mapping[str, str]) -> None:
    """
    Run Bernese Processing Engine [BPE] using the input arguments given in
    `bpe_env` as environment variables for the BPE runner script.

    Technically, Python runs Perl-program [the BPE runner] that initiates and
    starts BPE with given PCF and ampaign+session arguments.

    The function aborts if the needed environment variables are not present in
    the provided dictionary.

    """
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

    process: sub.Popen | None = None
    try:
        log.debug(f"Run BPE runner ...")
        process = sub.Popen(f"{pkg.bpe_runner}", env={**os.environ, **bpe_env})
        process.wait()
        log.debug(f"BPE runner finished ...")

    except KeyboardInterrupt:
        log.debug(f"BPE runner killed ...")

    finally:
        if process is not None:
            process.terminate()
            process.kill()
