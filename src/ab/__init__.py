"""
AutoBernese

"""
from importlib import metadata

import ab
from ab import configuration
import logging

__version__ = metadata.version(ab.__name__)

config = configuration.load()
logging.basicConfig(**config.get("logging"))
