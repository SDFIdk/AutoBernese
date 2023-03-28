"""
AutoBernese

"""
from importlib import metadata
import logging

import ab
from ab import configuration


__version__ = metadata.version(ab.__name__)
logging.basicConfig(**configuration.load().get("logging"))
