import json
from dataclasses import asdict

from ab.data import TransferStatus


def test_add_download_statusses():
    status1 = TransferStatus(1, 2)
    status2 = TransferStatus(2, 1)
    result = status1 + status2
    expected = TransferStatus(3, 3)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    status3 = TransferStatus(1, 2, 1, 2)
    status4 = TransferStatus(2, 1, 2, 1)
    result2 = status3 + status4
    expected2 = TransferStatus(3, 3, 3, 3)
    assert result2 == expected2, f"Expected {result2!r} to be {expected2!r} ..."


def test_radd_download_statusses():
    result = TransferStatus(1, 2)
    result += TransferStatus(2, 1)
    expected = TransferStatus(3, 3)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    result2 = TransferStatus(1, 2, 1, 2)
    result2 += TransferStatus(2, 1, 2, 1)
    expected2 = TransferStatus(3, 3, 3, 3)
    assert result2 == expected2, f"Expected {result2!r} to be {expected2!r} ..."


def test_download_status_asdict():
    result = asdict(TransferStatus(3, 3))
    expected = {
        "existing": 3,
        "downloaded": 3,
        "failed": 0,
        "not_found": 0,
        "exceptions": [],
    }
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
