"""
Package file paths

"""
from importlib import resources

import ab


base = resources.files(ab)

configuration = base.joinpath("autobernese.yaml")
bpe_runner = base.joinpath("bpe.pl")
