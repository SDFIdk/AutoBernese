"""
Shortcuts for reaching package data

"""

import pathlib
from importlib import resources

import ab


base = resources.files(ab)

configuration = base.joinpath("autobernese.yaml")
bpe_runner = base.joinpath("bpe.pl")
