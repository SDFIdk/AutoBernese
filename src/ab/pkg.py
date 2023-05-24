"""
Package file paths

"""
from importlib import resources

import ab


# Package root
base = resources.files(ab)

# Configuration module
env = base.joinpath("configuration/env.yaml")
configuration = base.joinpath("configuration/autobernese.yaml")

# Country codes
country_codes = base.joinpath("country_code/ISO-3166-1-alpha-3.yaml")

# Demo files
demo_sitelog = base.joinpath("demo/abmf_20211124.log")

# Station data
sta_template = base.joinpath("station/1.03.STA")

# Bernese GNSS Software API
bpe_runner = base.joinpath("bsw/bpe.pl")
campaign_template = base.joinpath("bsw/default.yaml")
campaign_header = base.joinpath("bsw/campaign_header.yaml")
campaign_list_template = base.joinpath("bsw/MENU_CMP.INP")
