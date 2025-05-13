from ab import __version__
from ab.bsw import get_bsw_release


def print_versions() -> None:
    print(f"AutoBernese version {__version__}; Bernese version {get_bsw_release()}")
