from __future__ import annotations

from typing import Any, Protocol

from reachkit.core.models import SourceResult


class SourceReader(Protocol):
    name: str

    def read(self, **kwargs: Any) -> SourceResult:
        ...
