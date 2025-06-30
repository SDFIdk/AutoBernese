import os


def divide() -> str:
    return "=" * os.get_terminal_size().columns


def title_divide(s: str, *, pad: int = 1) -> str:
    sz = os.get_terminal_size().columns
    if len(s) > sz - 2 * pad:
        return s
    eqs = "=" * (sz // 2 - pad - len(s) // 2)
    ostr = f"{eqs}{'':{pad}s}{s}{'':{pad}s}{eqs}"
    ostr += "=" * (sz - len(ostr))
    return ostr
