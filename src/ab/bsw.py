"""
API for Bernese GNSS Software

"""
from typing import Any
import subprocess as sub
import os

from ab.ressources import bpe_runner


KEYS_BPE: set[str] = {
    'AB_PCF_FILE',
    'AB_CPU_FILE',
    'AB_BPE_CAMPAIGN',
    'AB_YEAR',
    'AB_SESSION',
    'AB_SYSOUT',
    'AB_STATUS',
    'AB_TASKID',
}



def create_campaign(*args: list[Any], **kwargs: dict[Any, Any]) -> None:
    """
    Creates a campaign directory based on the specified template and adds the
    campaign path to the list of available campaigns in the corresponding menu.

    Args:



    """
    print("Creating campaign...")


def runbpe(**campaign) -> None:
    # keys_gotten = set(campaign)
    # diff = KEYS_BPE - keys_gotten
    # if diff:
    #     raise ValueError('PCF data missing {diff!r}')
    env = {**os.environ, **campaign}
    f = sub.Popen(f'{bpe_runner}', env=env)
