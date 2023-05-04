import yaml

from ab import (
    pkg,
    country_code,
)


def test_country_code():
    test_data = (
        # Function expects correctly formatted country names
        ("Denmark", "DNK"),
        ("France", "FRA"),
        ("Italy", "ITA"),
        # Country names are trimmed
        ("  Denmark ", "DNK"),
        ("  France ", "FRA"),
        ("  Italy ", "ITA"),
        # Function does not fix spelling mistakes
        ("denmark", None),
        ("france", None),
        ("italy", None),
        ("Neverland", None),
        ("Narnia", None),
        ("Madeuparupa", None),
    )
    for country_name, expected in test_data:
        result = country_code.get(country_name)
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    test_data_full = yaml.safe_load(pkg.country_codes.read_text())
    for country_name, expected in test_data_full.items():
        result = country_code.get(country_name)
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."
