from ab import __version__
from ab import pkg


def test_version():
    assert __version__ == "0.1.0"


def test_package_data_exist():
    assert pkg.bpe_runner.is_file()
    assert pkg.configuration.is_file()
    assert pkg.sta_template.is_file()
    assert pkg.country_codes.is_file()
    assert pkg.demo_sitelog.is_file()
    assert pkg.campaign_template.is_file()
    assert pkg.campaign_header.is_file()
