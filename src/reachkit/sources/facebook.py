from __future__ import annotations

from collections.abc import Callable
import json
import os
from urllib.parse import quote, urlencode

from reachkit.core.errors import ConfigError, ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text
from reachkit.runtime.limits import DEFAULT_LIMIT, MAX_LIMIT

FetchText = Callable[..., HttpResponse]


class FacebookGraphReader:
    name = "facebook"

    def __init__(self, fetcher: FetchText | None = None, token: str | None = None) -> None:
        self._fetcher = fetcher
        self._token = token

    def read(self, target: str) -> SourceResult:
        return self.page(target)

    def page(self, page_id: str) -> SourceResult:
        url = self._url(f"/{quote(page_id)}", {"fields": "id,name,about,link"})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        if not isinstance(data, dict):
            raise ParseError("Facebook page response was not an object")
        item = _page_item(data)
        return SourceResult(self.name, data.get("link"), item.title, response.headers.get("Content-Type"), [item], [])

    def feed(self, page_id: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        url = self._url(f"/{quote(page_id)}/feed", {"fields": "id,message,permalink_url,created_time", "limit": str(active_limit)})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        records = data.get("data") if isinstance(data, dict) else []
        items = [_feed_item(record) for record in list(records or [])[:active_limit] if isinstance(record, dict)]
        return SourceResult(self.name, url, f"Facebook feed: {page_id}", response.headers.get("Content-Type"), items, [])

    def search(self, query: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        url = self._url("/search", {"type": "page", "q": query, "fields": "id,name,link", "limit": str(active_limit)})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        records = data.get("data") if isinstance(data, dict) else []
        items = [_page_item(record) for record in list(records or [])[:active_limit] if isinstance(record, dict)]
        return SourceResult(self.name, url, f"Facebook search: {query}", response.headers.get("Content-Type"), items, [])

    def _url(self, path: str, params: dict[str, str]) -> str:
        token = self._token or os.environ.get("FACEBOOK_ACCESS_TOKEN")
        if not token:
            raise ConfigError("FACEBOOK_ACCESS_TOKEN is required")
        return "https://graph.facebook.com/v19.0" + path + "?" + urlencode({**params, "access_token": token})

    def _load_json(self, response: HttpResponse):
        try:
            return json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise ParseError("Facebook response was not valid JSON") from exc


def _page_item(data: dict) -> RetrievedItem:
    title = str(data.get("name") or data.get("id") or "Facebook page")
    lines = [title]
    if data.get("about"):
        lines.append(str(data.get("about")))
    return RetrievedItem(title=title, url=data.get("link"), text=compact_text("\n".join(lines)), metadata={"id": data.get("id")})


def _feed_item(data: dict) -> RetrievedItem:
    text = compact_text(str(data.get("message") or data.get("story") or data.get("id") or "Facebook post"))
    return RetrievedItem(
        title=data.get("id") or "Facebook post",
        url=data.get("permalink_url"),
        text=text,
        metadata={"id": data.get("id"), "created_time": data.get("created_time")},
    )
