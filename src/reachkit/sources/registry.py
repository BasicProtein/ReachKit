from __future__ import annotations

from reachkit.core.errors import InputError
from reachkit.sources.base import SourceReader


class SourceRegistry:
    def __init__(self) -> None:
        self._readers: dict[str, SourceReader] = {}

    def register(self, reader: SourceReader) -> None:
        self._readers[reader.name] = reader

    def get(self, name: str) -> SourceReader:
        try:
            return self._readers[name]
        except KeyError as exc:
            raise InputError("Unknown source") from exc

    def names(self) -> list[str]:
        return list(self._readers)


def default_registry() -> SourceRegistry:
    return SourceRegistry()
