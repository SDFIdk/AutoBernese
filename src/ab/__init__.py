"""
AutoBernese

"""
from importlib import metadata
import logging

import ab
from ab import configuration


__version__ = metadata.version(ab.__name__)
env = configuration.load().get("environment")
env.get("ab_root").mkdir(exist_ok=True)
env.get("logging").get("filename").touch()
logging.basicConfig(**env.get("logging"))
