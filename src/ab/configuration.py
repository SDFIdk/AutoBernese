"""
Configuration

"""
from importlib import (
    resources,
    metadata,
)
import pathlib
from typing import Any

import yaml
from yaml_env_tag import construct_env_tag

import ab

yaml.SafeLoader.add_constructor("!ENV", construct_env_tag)


# fname_autobernese = 'autobernese.yaml'
# ifname_default = pathlib.Path.home() / fname_autobernese

# ifname_candidates = (
#     ifname_
# )


# def load(fname: str | pathlib.Path = ifname_default) -> Any:
def load() -> Any:
    """
    Load built-in configuration file for AutoBernese.

    """
    # ifname = pathlib.Path(fname)
    # if not ifname.is_file():
    #     raise LookupError(f'Configuration file {ifname} does not exist ...')
    # return yaml.safe_load(ifname.read_text())
    ifname = resources.files(ab).joinpath("autobernese.yaml")
    return yaml.safe_load(ifname.read_text())
