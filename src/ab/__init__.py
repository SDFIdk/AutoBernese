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

# Get the path to the Bernese installation directory
bsw_path = config.get("bsw_path", ".")

# Note that a the path `.` makes the `.parent` property return itself.
env_path = pathlib.Path(bsw_path).parent

# Set filename path to the parent directory of the given installation path.
log_settings = config.get("logging")
log_settings["filename"] = env_path / log_settings.get("filename", "autobernese.log")

# Set global log settings for the root logger
logging.basicConfig(**log_settings)
