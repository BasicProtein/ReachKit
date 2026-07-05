from __future__ import annotations

from collections.abc import Callable
import json
import os
from urllib.parse import urlencode

from reachkit.core.errors import InputError, ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.html_text import html_to_text
from reachkit.normalization.text import compact_text
from reachkit.runtime.cookies import load_cookie_header
from reachkit.runtime.http import HttpResponse, fetch_text

FetchText = Callable[..., HttpResponse]


class WebReader:
    name = "web"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(
        self,
        url: str,
        max_chars: int | None = None,
        cookie_file: str | None = None,
        storage_state: str | None = None,
    ) -> SourceResult:
        active_fetcher = self._fetcher or fetch_text
        if cookie_file and storage_state:
            raise InputError("Use either cookie_file or storage_state, not both")
        cookie_source = cookie_file or storage_state
        headers = {"Cookie": load_cookie_header(cookie_source)} if cookie_source else None
        response = active_fetcher(url, headers=headers)
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


class WebSearchReader:
    name = "web"

    def __init__(self, fetcher: FetchText | None = None, endpoint: str | None = None) -> None:
        self._fetcher = fetcher
        self._endpoint = endpoint

    def search(self, query: str, limit: int = 10) -> SourceResult:
        endpoint = self._endpoint or os.environ.get("REACHKIT_WEB_SEARCH_URL")
        if not endpoint:
            raise InputError("REACHKIT_WEB_SEARCH_URL is required for web search")
        active_limit = max(1, min(limit, 50))
        separator = "&" if "?" in endpoint else "?"
        url = endpoint + separator + urlencode({"q": query, "limit": active_limit})
        response = (self._fetcher or fetch_text)(url)
        try:
            payload = json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise ParseError("Web search response was not valid JSON") from exc
        records = payload.get("items") if isinstance(payload, dict) else payload
        items: list[RetrievedItem] = []
        for record in list(records or [])[:active_limit]:
            if not isinstance(record, dict):
                continue
            title = str(record.get("title") or record.get("url") or "Web result")
            item_url = record.get("url") or record.get("link")
            text = compact_text(str(record.get("snippet") or record.get("text") or title))
            items.append(RetrievedItem(title=title, url=item_url, text=text, metadata={}))
        return SourceResult(self.name, url, f"Web search: {query}", response.headers.get("Content-Type"), items, [])
