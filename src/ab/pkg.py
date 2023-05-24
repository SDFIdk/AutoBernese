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
# TODO: Remove demo files, if not used
demo_sitelog = base.joinpath("demo/abmf_20211124.log")

# Template for the STA file generated from site-log files.
template_sta_file = base.joinpath("station/1.03.STA")

# Bernese GNSS Software API

# The script that runs Bernese Processing Engine with given input arguments
bpe_runner = base.joinpath("bsw/bpe.pl")

# Internal BSW file with the list of existing campaigns
template_campaign_menu_list = base.joinpath("bsw/MENU_CMP.INP")

# Template for the pre-processed meta data that are added to each campaign-configuration file.
campaign_header = base.joinpath("bsw/campaign_header.yaml")

# Campaign templates included in the package
# TODO: Make this a section in the documentation
template_campaign = base.joinpath("bsw/templates/default.yaml")
