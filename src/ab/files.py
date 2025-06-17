"""
Handle local data

"""

from pathlib import Path
import shutil
import logging


log = logging.getLogger(__name__)


def delete_directory_content(path: str) -> None:
    """
    Remove all children in a given directory.

    """
    for child in Path(path).iterdir():
        log.info(f"Deleting {child!r} ...")
        if child.is_file() or child.is_symlink():
            child.unlink()
        if child.is_dir():
            shutil.rmtree(child)
