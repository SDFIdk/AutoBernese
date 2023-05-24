"""
AutoBernese

"""
from importlib import metadata
import getpass
import logging

import ab
from ab import configuration


__version__ = metadata.version(ab.__name__)
env = configuration.load().get("environment")
env.get("autobernese").mkdir(exist_ok=True)
env.get("logging").get("filename").touch()
replacements = dict(
    format=env.get("logging").get("format").format(user=getpass.getuser()),
)
logging.basicConfig(**{**env.get("logging"), **replacements})
