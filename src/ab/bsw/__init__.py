"""
Module for Bernese GNSS Software system interaction.

"""

from dataclasses import dataclass

from ab import configuration


@dataclass
class ReleaseInfo:
    version: str
    release: str

    def __str__(self) -> str:
        return f"{self.version} ({self.release})"


def get_bsw_release() -> ReleaseInfo | None:
    config = configuration.load()
    fname = config.get("bsw_files", {}).get("release_info")
    if fname is None:
        return
    lines = fname.read_text().strip().splitlines()
    return ReleaseInfo(
        lines[0].split()[-1],
        lines[1].split()[-1],
    )
