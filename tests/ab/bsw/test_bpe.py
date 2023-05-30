import pytest

from ab.bsw.bpe import (
    as_environment_variables,
)


def test_as_environment_variables():
    whatever = ""
    _input = {
        "foo": whatever,
        "bar": whatever,
    }
    expected = {
        "AB_BPE_FOO": whatever,
        "AB_BPE_BAR": whatever,
    }
    result = as_environment_variables(_input)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    _input = {
        0: whatever,
    }
    with pytest.raises(TypeError):
        as_environment_variables(_input)

    _input = {
        "foo bar": whatever,
    }
    with pytest.raises(ValueError):
        as_environment_variables(_input)
