from __future__ import annotations

from collections.abc import Callable
import json
from urllib.parse import urlencode, urlparse

from reachkit.core.errors import ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text
from reachkit.runtime.limits import DEFAULT_LIMIT, MAX_LIMIT

FetchText = Callable[..., HttpResponse]


class RedditReader:
    name = "reddit"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def search(self, query: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        url = "https://www.reddit.com/search.json?" + urlencode({"q": query, "limit": active_limit})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        children = data.get("data", {}).get("children", []) if isinstance(data, dict) else []
        items = [_post_item(child.get("data", {})) for child in children[:active_limit] if isinstance(child, dict)]
        return SourceResult(self.name, url, f"Reddit search: {query}", response.headers.get("Content-Type"), items, [])

    def read(self, target: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        url = _json_url(target)
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        if not isinstance(data, list) or not data:
            raise ParseError("Reddit post response did not contain listings")
        items: list[RetrievedItem] = []
        post_children = data[0].get("data", {}).get("children", []) if isinstance(data[0], dict) else []
        for child in post_children[:1]:
            if isinstance(child, dict):
                items.append(_post_item(child.get("data", {})))
        comment_children = data[1].get("data", {}).get("children", []) if len(data) > 1 and isinstance(data[1], dict) else []
        for child in comment_children[: min(max(1, limit), MAX_LIMIT)]:
            if isinstance(child, dict) and isinstance(child.get("data"), dict):
                items.append(_comment_item(child["data"]))
        return SourceResult(self.name, target, items[0].title if items else "Reddit post", response.headers.get("Content-Type"), items, [])

    def _load_json(self, response: HttpResponse):
        try:
            return json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise ParseError("Reddit response was not valid JSON") from exc


def _json_url(target: str) -> str:
    parsed = urlparse(target)
    if parsed.scheme:
        base = target.rstrip("/")
        return base if base.endswith(".json") else f"{base}.json"
    return f"https://www.reddit.com/comments/{target}.json"


def _post_item(data: dict) -> RetrievedItem:
    title = str(data.get("title") or "Reddit post")
    permalink = data.get("permalink")
    url = f"https://www.reddit.com{permalink}" if isinstance(permalink, str) and permalink.startswith("/") else data.get("url")
    text = compact_text("\n".join(part for part in [title, str(data.get("selftext") or "")] if part))
    return RetrievedItem(title=title, url=url, text=text, metadata={"subreddit": data.get("subreddit"), "score": data.get("score")})


def _comment_item(data: dict) -> RetrievedItem:
    text = compact_text(str(data.get("body") or ""))
    permalink = data.get("permalink")
    url = f"https://www.reddit.com{permalink}" if isinstance(permalink, str) and permalink.startswith("/") else None
    return RetrievedItem(title=data.get("author") or "Reddit comment", url=url, text=text, metadata={"score": data.get("score")})
