from ab.data.source import (
    resolved,
)


def test_resolved():
    parameters = dict(a=(0, 1), b=(2, 3))
    expected = [
        dict(a=0, b=2),
        dict(a=0, b=3),
        dict(a=1, b=2),
        dict(a=1, b=3),
    ]
    result = resolved(parameters)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
