from pathlib import Path

import pytest

from ab.configuration import (
    _POP,
    merge,
    load,
)


def test_merge():
    dir_ = Path(__file__).parent / "configuration_files"
    ifname_1 = dir_ / "merge_1"
    ifname_2 = dir_ / "merge_2"

    expected = """\
merge_1

merge_2
"""

    # Nice input
    result = merge(ifname_1, ifname_2)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    # Duplicate filenames
    result = merge(ifname_1, ifname_2, ifname_1, str(ifname_2))
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    # Missing files
    ifname_missing = dir_ / "missing"
    with pytest.raises(RuntimeError) as info:
        merge(ifname_1, ifname_2, ifname_missing)

    # No files
    assert merge() == "", f"Expected no arguments to give an empty string ..."


def test_load():
    dir_ = Path(__file__).parent / "configuration_files"
    ifname_common = dir_ / "common.yaml"
    ifname_campaign = dir_ / "campaign.yaml"

    # Verify that core sections are removed, when filename is provided
    env_common = load(ifname_common)
    for key in _POP:
        assert (
            key not in env_common
        ), f"Expected {key!r} to not be in rendered configuration {ifname_common.stem!r}"

    # Any other section is allowed
    assert env_common.get("troposphere") is not None

    # Verify that core sections are available
    env_campaign = load(ifname_campaign, keep_env=True)
    for key in _POP:
        assert (
            key in env_campaign
        ), f"Expected {key!r} to be in rendered configuration {ifname_campaign.stem}"

    # Verify that section is overridden
    env_common_campaign = load(ifname_common, ifname_campaign)
    expected = env_campaign.get("troposphere").get("ipath")
    result = env_common_campaign.get("troposphere").get("ipath")
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_load_arbitrary_configurations():
    import yaml

    dir_ = Path(__file__).parent / "configuration_files"
    ifname_a = dir_ / "a.yaml"
    ifname_b = dir_ / "b.yaml"
    ifname_c = dir_ / "c.yaml"

    a = yaml.safe_load(ifname_a.read_text())
    s_a_b = ifname_a.read_text() + "\n" + ifname_b.read_text()
    a_b = yaml.safe_load(s_a_b)
    s_a_b_c = (
        ifname_a.read_text() + "\n" + ifname_b.read_text() + "\n" + ifname_c.read_text()
    )
    a_b_c = yaml.safe_load(s_a_b_c)

    # from IPython import embed
    # embed()
