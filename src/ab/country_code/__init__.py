"""
Three-letter country codes

"""

import functools

import yaml

from ab import pkg


_COUNTRY_CODES: dict[str, str] = None


@functools.cache
def get(country_name: str) -> str:
    """
    Get three-letter country code for given country name if it exists in the
    package-version of the ISO 3166 standard.

    References:
    -----------
    *   [ISO 3166 Country Codes](https://www.iso.org/iso-3166-country-codes.html)

    """
    global _COUNTRY_CODES
    if _COUNTRY_CODES is None:
        _COUNTRY_CODES = yaml.safe_load(pkg.country_codes.read_text())
    return _COUNTRY_CODES.get(country_name.strip())
