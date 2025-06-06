from ab.parameters import (
    permutations,
    resolvable,
)


def test_permutations():
    parameters = dict(a=(0, 1), b=(2, 3))
    expected = [
        dict(a=0, b=2),
        dict(a=0, b=3),
        dict(a=1, b=2),
        dict(a=1, b=3),
    ]
    result = permutations(parameters)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_resolvable():
    parameters = dict(a=1, b=2)
    template = "{a}{a.bit_count()}"
    expected = dict(a=1)
    result = resolvable(parameters, template)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
