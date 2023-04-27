"""
Module for Bernese GNSS Software interaction.

API for the Bernese GNSS Software system

"""
from typing import (
    Any,
    Mapping,
)
import subprocess as sub
import os
import logging

from ab import pkg
from ab.bsw import campaign


log = logging.getLogger(__name__)

SETTINGS_DEFAULT_BPE: dict[str, str] = dict(
    ab_bpe_pcf_file="PPP",
    ab_bpe_cpu_file="USER",
    ab_bpe_bpe_campaign="EXAMPLE",
    ab_bpe_year="2019",
    ab_bpe_session="0440",
    ab_bpe_sysout="PPP",
    ab_bpe_status="PPP.RUN",
    ab_bpe_taskid="PP",
)
KEYS_BPE: set[str] = set(SETTINGS_DEFAULT_BPE)


def create_campaign(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Creates a campaign directory based on the specified template and adds the
    campaign path to the list of available campaigns in the corresponding menu.

    """
    log.debug("Creating campaign...")
    campaign.create()


def runbpe(bpe_settings: Mapping) -> None:
    f"""
    Start specified Proces Control File with Bernese Processing Engine [BPE].

    Technically, Python runs Perl-program that initiates and starts BPE with
    given PCF.

    Parameters: {', '.join(SETTINGS_DEFAULT_BPE.keys())}

    """
    if not bpe_settings:
        log.debug("Use default BPE settings ...")
        # TODO: Break here instead of running the EXAMPLE campaign
        bpe_settings = SETTINGS_DEFAULT_BPE

    keys_gotten = set(bpe_settings)
    diff = KEYS_BPE - keys_gotten
    if diff:
        msg = "PCF data missing {diff!r}"
        log.debug(msg)
        raise ValueError(msg)

    log.info(f"Using the following PCF metadata as input:")
    sz = max(len(key) for key in bpe_settings)
    for key, value in bpe_settings.items():
        log.info(f"{key: <{sz}s}: {value}")
    try:
        log.debug(f"Run BPE runner ...")
        process = sub.Popen(f"{pkg.bpe_runner}", env={**os.environ, **bpe_settings})
        process.wait()
        log.debug(f"BPE runner finished ...")

    except KeyboardInterrupt:
        process.terminate()
        process.kill()
        log.debug(f"BPE runner killed ...")
