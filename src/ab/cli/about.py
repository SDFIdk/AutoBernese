"""
Get information about Bernese GNSS Software and AutoBernese

"""

from rich import print

from ab import __version__
from ab.bsw import get_bsw_release


def autobernese() -> str:
    return f"AutoBernese {__version__}"


def bernese() -> str:
    return f"Bernese {get_bsw_release()}"


def versions() -> str:
    return f"{autobernese()}; {bernese()}"


def print_versions() -> None:
    print(versions())
