"""
Run the Bernese Processing Engine [BPE]

"""

import os
import logging
import subprocess as sub

from ab import pkg
from ab.bsw.bpe_terminal_output import parse_bpe_terminal_output


log = logging.getLogger(__name__)


def ensure_string(s: str) -> str:
    if not isinstance(s, str):
        TypeError("Expected {s!r} to be `str` ...")
    return s


# def run_bpe(**parameters: dict[str, str]) -> object:
def run_bpe(
    pcf_file: str,
    campaign: str,
    year: str,
    session: str,
    sysout: str,
    status: str,
    taskid: str,
    cpu_file: str = "USER",
) -> object:
    """
    Run Bernese Processing Engine [BPE] by setting needed environment variables
    for the built-in BPE runner script `bpe.pl` that initiates and starts BPE
    with given PCF and campaign + session arguments.

    """
    bpe_env = dict(
        AB_BPE_PCF_FILE=ensure_string(pcf_file),
        AB_BPE_CAMPAIGN=ensure_string(campaign),
        AB_BPE_YEAR=ensure_string(year),
        AB_BPE_SESSION=ensure_string(session),
        AB_BPE_SYSOUT=ensure_string(sysout),
        AB_BPE_STATUS=ensure_string(status),
        AB_BPE_TASKID=ensure_string(taskid),
        AB_BPE_CPU_FILE=ensure_string(cpu_file),
    )

    log.info(f"Using the following PCF metadata as input:")
    sz = max(len(key) for key in bpe_env)
    for key, value in bpe_env.items():
        log.info(f"{key: <{sz}s}: {value}")

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
        for line in process.stdout:  # type: ignore
            output += line
            log.info(line.strip())

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
