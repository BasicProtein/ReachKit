from __future__ import annotations

from collections.abc import Callable

from reachkit.core.errors import ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.html_text import html_to_text
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text

FetchText = Callable[..., HttpResponse]


class WebReader:
    name = "web"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(self, url: str, max_chars: int | None = None) -> SourceResult:
        active_fetcher = self._fetcher or fetch_text
        response = active_fetcher(url)
        content_type = response.headers.get("Content-Type") or response.headers.get("content-type")
        media_type = (content_type or "").split(";", 1)[0].strip().lower()
        warnings: list[str] = []

        if media_type == "text/html":
            text, title = html_to_text(response.body)
            text = compact_text(text, max_chars=max_chars)
        elif media_type == "text/plain":
            title = None
            text = compact_text(response.body, max_chars=max_chars)
        elif media_type.startswith("text/"):
            title = None
            text = compact_text(response.body, max_chars=max_chars)
            warnings.append("non_html_text")
        else:
            raise ParseError("Content type is not readable text")

        if not text:
            raise ParseError("Readable text is empty")

        item = RetrievedItem(title=title, url=response.url, text=text, metadata={})
        return SourceResult(
            source=self.name,
            url=response.url,
            title=title,
            content_type=content_type,
            items=[item],
            warnings=warnings,
        )
