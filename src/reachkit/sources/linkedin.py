from __future__ import annotations

from collections.abc import Callable

from reachkit.core.errors import InputError
from reachkit.core.models import SourceResult
from reachkit.runtime.http import HttpResponse
from reachkit.sources.web import WebReader

FetchText = Callable[..., HttpResponse]


class LinkedInPublicReader:
    name = "linkedin"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(self, target: str) -> SourceResult:
        if "linkedin.com" not in target.lower():
            raise InputError("LinkedIn public reader requires a LinkedIn URL")
        result = WebReader(fetcher=self._fetcher).read(target)
        return SourceResult(self.name, result.url, result.title, result.content_type, result.items, result.warnings)
