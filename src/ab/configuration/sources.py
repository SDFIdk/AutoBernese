"""
Configuration tools to build Source instances

"""

from typing import Any

from ab.configuration import SectionListItemType
from ab.data.source import Source


def load(kwargs: SectionListItemType) -> Source:
    return Source(**kwargs)


def load_all(raw: list[SectionListItemType]) -> list[Source]:
    return [load(kwargs) for kwargs in raw]
