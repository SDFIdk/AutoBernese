from ab import __version__
from ab import pkg


def test_version():
    assert __version__ == "0.4.1"


def test_package_data_exist():
    assert pkg.env.is_file()

    assert pkg.country_codes.is_file()

    assert pkg.template_sta_file.is_file()

    assert pkg.bpe_runner.is_file()
    assert pkg.template_campaign_menu_list.is_file()
    assert pkg.template_campaign_default.is_file()
    assert pkg.campaign_header.is_file()
