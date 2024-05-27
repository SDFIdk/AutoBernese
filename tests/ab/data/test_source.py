from pathlib import Path

from ab.data.source import Source


def test_create_Source_using_strings():

    # Arrange
    identifier: str = "SOURCE"
    description: str = "DESCRIPTION"
    url: str | Path = "file:///path/to/file.txt"
    destination: str | Path = "file:///path/to/destination"

    # Act
    source = Source(
        identifier,
        description,
        url,
        destination,
    )

    # Assert
    result = source.url_
    expected = "file:///path/to/file.txt"
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    result = source.destination_
    expected = "file:/path/to/destination"
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    result = source.protocol
    expected = "file"
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_create_Source_using_Path_instances():

    # Arrange
    identifier: str = "SOURCE"
    description: str = "DESCRIPTION"
    url: str | Path = Path("file:///path/to/file.txt")
    destination: str | Path = Path("file:///path/to/destination")

    # Act
    source = Source(
        identifier,
        description,
        url,
        destination,
    )

    # Expected
    url_ = "file:/path/to/file.txt"

    # Assert
    result = source.url_
    expected = url_
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
