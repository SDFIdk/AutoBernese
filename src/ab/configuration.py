"""
Configuration

"""
import pathlib
from typing import Any

import yaml


fname_autobernese = 'autobernese.yaml'
ifname_default = pathlib.Path.home() / fname_autobernese

# ifname_candidates = (
#     ifname_
# )


def load(fname: str | pathlib.Path = ifname_default) -> Any:
    """
    Load a configuration file for AutoBernese.

    """
    ifname = pathlib.Path(fname)
    if not ifname.is_file():
        raise LookupError(f'Configuration file {ifname} does not exist ...')
    return yaml.safe_load(ifname.read_text())
