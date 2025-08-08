from ab.strings import Operator


def test_Operator():
    s = Operator("a")

    expected = "A"
    result = s.operate("upper")

    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    expected = ["a"]
    result = s.operate("split", "-")

    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    expected = "-a-"
    result = s.operate("join", ["-", "-"])

    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
