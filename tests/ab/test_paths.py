from pathlib import Path

from ab.paths import resolve_wildcards


def test_resolve_wildcards_with_wildcards(tmp_path):

    # Arrange
    fnames = [
        "foo_x.bar",
        "foo_y.bar",
        "foo_z.bar",
    ]
    ifnames = [tmp_path / fname for fname in fnames]
    [ifname.touch() for ifname in ifnames]

    expected = [ifname.name for ifname in ifnames]

    # Act
    path_input = Path(tmp_path / "foo*.bar")
    result = list(resolve_wildcards(path_input))

    # Assert
    for ifname in result:
        assert (
            ifname.name in expected
        ), f"Expected {ifname.name} to be in {expected!r} ..."


def test_directories_with_trailing_slash(tmp_path):

    # Arrange
    directories = "ABC"
    paths = [tmp_path / directory for directory in directories]
    [path.mkdir() for path in paths]

    expected = directories

    # Act
    path_input = Path(tmp_path / "*/")
    result = list(resolve_wildcards(path_input))

    # Assert
    for path in result:
        assert path.name in expected, f"Expected {path.name} to be in {expected!r} ..."


def test_directories_no_trailing_slash(tmp_path):

    # Arrange
    directories = "ABC"
    fname_in_A = "foo.bar"
    paths = [tmp_path / directory for directory in directories]
    [path.mkdir() for path in paths]
    (paths[0] / fname_in_A).touch()

    expected = directories

    # Act
    path_input = Path(tmp_path / "*")
    result = list(resolve_wildcards(path_input))

    # Assert
    for path in result:
        assert path.name in expected, f"Expected {path.name} to be in {expected!r} ..."


def test_file_in_dir(tmp_path):

    # Arrange
    directories = "ABC"
    paths = [tmp_path / directory for directory in directories]
    [path.mkdir() for path in paths]

    fname_in_A = "foo.bar"
    ifname_in_A = paths[0] / fname_in_A
    ifname_in_A.touch()

    expected = ifname_in_A

    # Act I
    path_input = Path(tmp_path / "**" / "*.bar")
    result = list(resolve_wildcards(path_input))

    # Assert
    ifname = result[0]
    assert (
        ifname.name == expected.name
    ), f"Expected {ifname.name} to be {expected.name!r} ..."

    # Act II
    path_input = Path(tmp_path / "**" / "foo.bar")
    result = list(resolve_wildcards(path_input))

    # Assert
    ifname = result[0]
    assert (
        ifname.name == expected.name
    ), f"Expected {ifname.name} to be {expected.name!r} ..."

    # Act III
    path_input = Path(tmp_path / "A" / "foo.bar")
    result = list(resolve_wildcards(path_input))

    # Assert
    ifname = result[0]
    assert (
        ifname.name == expected.name
    ), f"Expected {ifname.name} to be {expected.name!r} ..."


def test_resolve_wildcards_without_wildcards(tmp_path):
    ifname = tmp_path / "foo.bar"
    ifname.touch()

    expected = [ifname]
    result = list(resolve_wildcards(ifname))
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_empty_result_for_non_existing_file():
    ifname = Path("foo.bar")
    expected = []
    result = list(resolve_wildcards(ifname))
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
