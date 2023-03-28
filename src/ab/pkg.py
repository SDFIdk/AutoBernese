"""
Package file paths

"""
from importlib import resources

import ab


base = resources.files(ab)

configuration = base.joinpath("autobernese.yaml")
bpe_runner = base.joinpath("bpe.pl")

sta_template = base.joinpath("templates/1.03.STA")


demo_sitelog = base.joinpath("demo/esbc00dnk_20221113.log")
