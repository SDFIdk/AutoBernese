"""
Package file paths

"""
from importlib import resources

import ab


base = resources.files(ab)

configuration = base.joinpath("autobernese.yaml")
bpe_runner = base.joinpath("bpe.pl")
country_codes = base.joinpath("ISO-3166-1-alpha-3.yaml")

sta_template = base.joinpath("templates/1.03.STA")

demo_sitelog = base.joinpath("demo/abmf_20211124.log")
