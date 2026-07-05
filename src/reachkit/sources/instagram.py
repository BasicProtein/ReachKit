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


class InstagramGraphReader:
    name = "instagram"

    def __init__(self, fetcher: FetchText | None = None, token: str | None = None) -> None:
        self._fetcher = fetcher
        self._token = token

    def read(self, target: str) -> SourceResult:
        return self.profile(target)

    def profile(self, user_id: str) -> SourceResult:
        url = self._url(f"/{quote(user_id)}", {"fields": "id,username,name,biography,website"})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        if not isinstance(data, dict):
            raise ParseError("Instagram profile response was not an object")
        item = _profile_item(data)
        return SourceResult(self.name, None, item.title, response.headers.get("Content-Type"), [item], [])

    def media(self, user_id: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        url = self._url(f"/{quote(user_id)}/media", {"fields": "id,caption,permalink,timestamp,media_type", "limit": str(active_limit)})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        records = data.get("data") if isinstance(data, dict) else []
        items = [_media_item(record) for record in list(records or [])[:active_limit] if isinstance(record, dict)]
        return SourceResult(self.name, url, f"Instagram media: {user_id}", response.headers.get("Content-Type"), items, [])

    def search(self, query: str, user_id: str) -> SourceResult:
        url = self._url("/ig_hashtag_search", {"user_id": user_id, "q": query})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        records = data.get("data") if isinstance(data, dict) else []
        items = [_hashtag_item(record) for record in list(records or []) if isinstance(record, dict)]
        return SourceResult(self.name, url, f"Instagram hashtag search: {query}", response.headers.get("Content-Type"), items, [])

    def _url(self, path: str, params: dict[str, str]) -> str:
        token = self._token or os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        if not token:
            raise ConfigError("INSTAGRAM_ACCESS_TOKEN is required")
        return "https://graph.facebook.com/v19.0" + path + "?" + urlencode({**params, "access_token": token})

    def _load_json(self, response: HttpResponse):
        try:
            return json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise ParseError("Instagram response was not valid JSON") from exc


def _profile_item(data: dict) -> RetrievedItem:
    title = str(data.get("username") or data.get("name") or data.get("id") or "Instagram profile")
    lines = [title]
    for key in ("name", "biography", "website"):
        if data.get(key):
            lines.append(str(data.get(key)))
    return RetrievedItem(title=title, url=data.get("website"), text=compact_text("\n".join(lines)), metadata={"id": data.get("id")})


def _media_item(data: dict) -> RetrievedItem:
    title = str(data.get("id") or "Instagram media")
    text = compact_text(str(data.get("caption") or title))
    return RetrievedItem(title=title, url=data.get("permalink"), text=text, metadata={"id": data.get("id"), "media_type": data.get("media_type")})


def _hashtag_item(data: dict) -> RetrievedItem:
    title = str(data.get("name") or data.get("id") or "Instagram hashtag")
    return RetrievedItem(title=title, url=None, text=compact_text(title), metadata={"id": data.get("id")})
