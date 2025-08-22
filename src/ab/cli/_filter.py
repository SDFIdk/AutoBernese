"""
Command-line helper for filtering list items

"""

import logging

from ab.configuration import (
    ConfigurationType,
    SectionListItemType,
)


log = logging.getLogger(__name__)


def get_raw(
    config: ConfigurationType,
    section: str,
    identifiers: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[SectionListItemType]:
    """
    Get items in sections `sources` or `tasks` and take all or selected.

    """
    raw: list[SectionListItemType] = config.get(section, [])
    if not raw:
        msg = f"No {section} found ..."
        print(msg)
        log.info(msg)

    if identifiers is not None and len(identifiers) > 0:
        raw = [
            raw_item for raw_item in raw if raw_item.get("identifier") in identifiers
        ]

    if exclude is not None and len(exclude) > 0:
        raw = [
            raw_item for raw_item in raw if raw_item.get("identifier") not in exclude
        ]

    return raw
