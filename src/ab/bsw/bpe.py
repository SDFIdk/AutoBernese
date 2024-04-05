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
    field,
)
from string import Template
import datetime as dt

from ab import pkg
from ab.parameters import (
    resolvable,
    resolved,
)


log = logging.getLogger(__name__)


@dataclass
class BPETerminalOutput:
    """
    Container for result printed in the terminal:

    """

    beg: dt.datetime
    username: str
    pcf_file: str
    cpu_file: str
    campaign: str
    year_session: str
    output_file: str
    status_file: str
    server_pid: str
    end: dt.datetime
    ok: bool = True


@dataclass
class BPETaskArguments:
    """
    Specification for BPE task arguments needed for running a BPE task.

    """

    pcf_file: str
    campaign: str
    year: str
    session: str
    sysout: str
    status: str
    taskid: str
    cpu_file: str = "USER"


@dataclass
class BPETaskRunner:
    arguments: dict[str, str]

    def run(self) -> BPETerminalOutput:
        return run_bpe(as_environment_variables(self.arguments))


@dataclass
class BPETask:
    """
    A BPETask instance is a compact specification containing the needed
    information for running a given Process Control File with different input
    combinations.

    """

    identifier: str
    description: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Iterable[Any]] | None = None

    def __post_init__(self) -> None:
        """
        Alleviate user from having to specify explicitly what type of arguments
        to use by creating an instance of `_BPETaskArguments` that specify
        needed arguments for the BPE.

        BPE task arguments contains the input needed for running a BPE task.

        The members can be used as is, e.g.

        ``` instance = _BPETaskArguments(...)
        run_bpe(as_environment_variables(asdict(instance))) ```

        Alternatively, each member can be a template string that can be resolved
        using the method `resolve` and given a dictionary of parameters that fit
        the template.

        """
        self._arguments: BPETaskArguments = BPETaskArguments(**self.arguments)

    def resolve(self) -> list[dict[str, str]]:
        """
        Returns a list of dictionaries with the BPE-argument names as keys and
        the corresponding values a possible combination of the given parameters.

        Create every possible expansion of any template strings in the
        instance's `arguments` given the parameters of the instance.

        """
        if self.parameters is None:
            return []

        arguments = asdict(self._arguments)
        return [
            {
                # Re-format the string contained in `value` using only the
                # parameters used in the string.
                key: value.format(**resolvable(combination, value))
                for (key, value) in arguments.items()
            }
            # Here, we are getting a list with each possible permutation of the
            # given parameters.
            for combination in resolved(self.parameters)
        ]

    def runners(self) -> BPETaskRunner:
        return [BPETaskRunner(resolved) for resolved in self.resolve()]


def parse_bpe_terminal_output(
    raw: str, substitutes: dict[str, str] | None = None
) -> BPETerminalOutput:
    if substitutes is not None:
        raw = Template(raw).safe_substitute(substitutes)
    lines = [line.strip() for line in raw.splitlines() if line.strip() != ""]
    kwargs = {}
    for line in lines:
        if line.startswith("Starting BPE on "):
            kwargs["beg"] = dt.datetime.strptime(line[-20:], "%d-%b-%Y %H:%M:%S")
            continue
        if line.endswith("@"):
            kwargs["username"] = line[:-1]
            continue
        if line.startswith("PCFile:"):
            kwargs["pcf_file"] = line.split("PCFile:")[-1].strip()
            continue
        if line.startswith("CPU file:"):
            kwargs["cpu_file"] = line.split("CPU file:")[-1].strip()
            continue
        if line.startswith("Campaign:"):
            kwargs["campaign"] = line.split("Campaign:")[-1].strip()
            continue
        if line.startswith("Year/session:"):
            kwargs["year_session"] = line.split("Year/session:")[-1].strip()
            continue
        if line.startswith("BPE output:"):
            kwargs["output_file"] = line.split("BPE output:")[-1].strip()
            continue
        if line.startswith("BPE status:"):
            kwargs["status_file"] = line.split("BPE status:")[-1].strip()
            continue
        if line.startswith("BPE server runs PID ="):
            kwargs["server_pid"] = line.split("BPE server runs PID =")[-1].strip()
            continue
        if line.startswith("BPE finished") or line.startswith("BPE error"):
            kwargs["end"] = dt.datetime.strptime(line[-20:], "%d-%b-%Y %H:%M:%S")
            continue
        if line.startswith("User script error"):
            kwargs["ok"] = False
    return BPETerminalOutput(**kwargs)


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

    Technically, Python runs the AutoBernese Perl-program `bpe.pl` that
    initiates and starts BPE with given PCF and campaign + session arguments.

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

    # process: sub.Popen | None = None
    # try:
    #     log.debug(f"Run BPE runner ...")
    #     # process = sub.Popen(f"{pkg.bpe_runner}", env={**os.environ, **bpe_env})
    #     # process.wait()
    #     process = sub.Popen(
    #         f"{pkg.bpe_runner}",
    #         env={**os.environ, **bpe_env},
    #         stdout=sub.PIPE,
    #         stderr=sub.STDOUT,
    #         universal_newlines=True,
    #     )
    #     out, err = process.communicate()
    #     log.debug(f"BPE runner finished ...")
    #     return parse_bpe_terminal_output(out)

    # except KeyboardInterrupt:
    #     log.debug(f"BPE runner killed ...")
    #     # Re-raise so that external caller can adapt accordingly
    #     raise

    # finally:
    #     if process is not None:
    #         process.terminate()
    #         process.kill()

    process: sub.Popen | None = None
    try:
        log.debug(f"Run BPE runner ...")
        process = sub.Popen(
            f"{pkg.bpe_runner}",
            env={**os.environ, **bpe_env},
            stdout=sub.PIPE,
            stderr=sub.STDOUT,
            universal_newlines=True,
        )
        output = ""
        for line in process.stdout:
            output += line
            print(line, end="")

        log.debug(f"BPE runner finished ...")
        return parse_bpe_terminal_output(output)

    except KeyboardInterrupt:
        log.debug(f"BPE runner killed ...")
        # Re-raise so that external caller can adapt accordingly
        raise

    finally:
        if process is not None:
            process.terminate()
            process.kill()
