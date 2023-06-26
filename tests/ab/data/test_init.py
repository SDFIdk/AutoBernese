import json

from ab.data import DownloadStatus


def test_add_download_statusses():
    status1 = DownloadStatus(1, 2)
    status2 = DownloadStatus(2, 1)
    result = status1 + status2
    expected = DownloadStatus(3, 3)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_radd_download_statusses():
    result = DownloadStatus(1, 2)
    result += DownloadStatus(2, 1)
    expected = DownloadStatus(3, 3)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_download_status_repr():
    result = DownloadStatus(3, 3).asdict()
    expected = {
        "existing": 3,
        "downloaded": 3
    }
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
