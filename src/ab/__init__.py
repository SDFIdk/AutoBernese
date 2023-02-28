"""
AutoBernese

"""
from importlib import metadata

import ab
from ab import configuration

__version__ = metadata.version(ab.__name__)

log_yaml = configuration.load()
# Here should follow parsing of the entire configuration
