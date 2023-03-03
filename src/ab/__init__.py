"""
AutoBernese

"""
from importlib import metadata
import logging
import pathlib

import ab
from ab import configuration

__version__ = metadata.version(ab.__name__)

config = configuration.load()

# Set up logging
log_kwargs = config.get("logging")
bsw_path = config.get("bsw_path")  # Get the path to the Bernese installation directory
env_path = pathlib.Path(bsw_path).parent
log_kwargs["filename"] = env_path / log_kwargs.get("filename", "autobernese.log")
logging.basicConfig(**log_kwargs)  # Set up basic logging using the loaded configuration
