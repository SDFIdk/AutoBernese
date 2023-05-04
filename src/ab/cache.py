"""
Module with cache functionality

"""
from pathlib import Path
from typing import Any

import yaml


class KeyValueCache:
    def __init__(self, fname: Path | str) -> None:
        self.fname = Path(fname)
        self.fname.touch()

    def _load(self) -> dict[str, list[str]]:
        return yaml.safe_load(self.fname.read_text()) or {}

    def _save(self, updated: dict[str, list[str]]) -> None:
        self.fname.write_text(yaml.dump(updated))

    def __contains__(self, key: str) -> bool:
        return key in self._load()

    def __getitem__(self, key: str) -> list[str]:
        return self._load().get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self._save({**self._load(), **{key: value}})
