from pathlib import Path

from ab.configuration.yaml_constructors import (
    resolve_wildcards,
)


def test_resolve_wildcards_with_wildcards(tmp_path):
    """
    Note that this test does some processing of the result it gets from the
    tested function.

    On GitHub, the order of the files returnes were different, all though the
    content of the list was the same.

    As this seems to be a problem elsewhere, the extra processing is not added
    to the function to be tested iteself, but only to the test function.

    The reason for this is that the test contains a small set of files, whereas
    the use of the function ould potentially yield many filenames that it wuold
    take long to sort and whih also would violate the efficacy of the returned
    generator that `Path.glob` returns.

    """

    # Arrange
    fnames = [
        "foo_x.bar",
        "foo_y.bar",
        "foo_z.bar",
    ]
    [(tmp_path / fname).touch() for fname in fnames]

    list_sorted = lambda iterable: list(sorted(iterable))

    expected = list_sorted(tmp_path / fname for fname in fnames)

    path = Path(tmp_path / "foo*.bar")

    # Act
    result = list_sorted(resolve_wildcards(path))

    # Assert
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_resolve_wildcards_without_wildcards():
    fname = "foo.bar"
    path = Path(fname)
    expected = [Path(fname)]
    result = list(resolve_wildcards(path))
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
