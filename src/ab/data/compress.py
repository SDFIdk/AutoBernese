"""
File compression

"""

from pathlib import Path

import shutil
import gzip as _gzip


def gzip(fname: str | Path) -> None:
    ifname = Path(fname)
    if not ifname.is_file():
        raise IOError(f"File {fname!r} does not exist ...")
    ofname = ifname.with_suffix(ifname.suffix + ".gz")
    # From: https://docs.python.org/3.12/library/gzip.html
    with open(ifname, "rb") as f_in:
        with _gzip.open(ofname, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
