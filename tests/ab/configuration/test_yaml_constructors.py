from pathlib import Path

from ab.configuration.yaml_constructors import (
    resolve_wildcards,
)


def test_resolve_wildcards_with_wildcards(tmp_path):
    # Arrange
    fnames = (
        "foo_x.bar",
        "foo_y.bar",
        "foo_z.bar",
    )
    [(tmp_path / fname).touch() for fname in fnames]

    expected = [tmp_path / fname for fname in fnames]

    path = Path(tmp_path / "foo*.bar")

    # Act
    result = list(resolve_wildcards(path))

    # Assert
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_resolve_wildcards_without_wildcards():
    fname = "foo.bar"
    path = Path(fname)
    expected = [Path(fname)]
    result = list(resolve_wildcards(path))
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
