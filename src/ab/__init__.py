"""
AutoBernese

"""
from importlib import metadata
import getpass
import logging

import ab
from ab import configuration


__version__ = metadata.version(ab.__name__)
runtime = configuration.load().get("runtime")
runtime.get("ab").mkdir(exist_ok=True)
log_kw = runtime.get("logging")
log_kw.get("filename").touch()
replacements = dict(
    format=log_kw.get("format").format(user=getpass.getuser()),
)
logging.basicConfig(**{**log_kw, **replacements})
