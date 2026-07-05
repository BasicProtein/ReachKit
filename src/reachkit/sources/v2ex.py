from __future__ import annotations

from collections.abc import Callable
import json
from urllib.parse import quote, urlencode

from reachkit.core.errors import InputError, ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text
from reachkit.runtime.limits import DEFAULT_LIMIT, MAX_LIMIT

FetchText = Callable[..., HttpResponse]


class V2EXReader:
    name = "v2ex"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(self, target: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        if target == "hot":
            return self.hot(limit=limit)
        if target.startswith("node:"):
            return self.node(target.split(":", 1)[1], limit=limit)
        if target.startswith("topic:"):
            return self.topic(int(target.split(":", 1)[1]), include_replies=True, limit=limit)
        if target.startswith("user:"):
            return self.user(target.split(":", 1)[1])
        raise InputError("V2EX target must be hot, node:<name>, topic:<id>, or user:<name>")

    def hot(self, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        url = "https://www.v2ex.com/api/topics/hot.json"
        response = (self._fetcher or fetch_text)(url)
        records = self._load_json(response)
        items = [_topic_item(record) for record in list(records or [])[:active_limit] if isinstance(record, dict)]
        return SourceResult(self.name, url, "V2EX hot topics", response.headers.get("Content-Type"), items, [])

    def node(self, name: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        url = "https://www.v2ex.com/api/topics/show.json?" + urlencode({"node_name": name})
        response = (self._fetcher or fetch_text)(url)
        records = self._load_json(response)
        items = [_topic_item(record) for record in list(records or [])[:active_limit] if isinstance(record, dict)]
        return SourceResult(self.name, url, f"V2EX node: {name}", response.headers.get("Content-Type"), items, [])

    def topic(self, topic_id: int, include_replies: bool = False, limit: int = DEFAULT_LIMIT) -> SourceResult:
        url = "https://www.v2ex.com/api/topics/show.json?" + urlencode({"id": topic_id})
        response = (self._fetcher or fetch_text)(url)
        records = self._load_json(response)
        first = list(records or [])[0] if isinstance(records, list) and records else {}
        if not isinstance(first, dict):
            raise ParseError("V2EX topic response did not contain a topic")
        items = [_topic_item(first)]
        if include_replies:
            items.extend(self._replies(topic_id, limit=limit))
        return SourceResult(self.name, url, f"V2EX topic {topic_id}", response.headers.get("Content-Type"), items, [])

    def user(self, username: str) -> SourceResult:
        url = "https://www.v2ex.com/api/members/show.json?" + urlencode({"username": username})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        if not isinstance(data, dict):
            raise ParseError("V2EX user response was not an object")
        title = str(data.get("username") or username)
        lines = [title]
        for key in ("tagline", "bio", "website", "github"):
            if data.get(key):
                lines.append(str(data.get(key)))
        item = RetrievedItem(
            title=title,
            url=data.get("url") or f"https://www.v2ex.com/member/{quote(username)}",
            text=compact_text("\n".join(lines)),
            metadata={"username": title},
        )
        return SourceResult(self.name, item.url, title, response.headers.get("Content-Type"), [item], [])

    def _load_json(self, response: HttpResponse):
        try:
            return json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise ParseError("V2EX response was not valid JSON") from exc

    def _replies(self, topic_id: int, limit: int = DEFAULT_LIMIT) -> list[RetrievedItem]:
        active_limit = min(max(1, limit), MAX_LIMIT)
        url = "https://www.v2ex.com/api/replies/show.json?" + urlencode({"topic_id": topic_id})
        response = (self._fetcher or fetch_text)(url)
        records = self._load_json(response)
        return [_reply_item(record) for record in list(records or [])[:active_limit] if isinstance(record, dict)]


def _topic_item(data: dict) -> RetrievedItem:
    node = data.get("node") if isinstance(data.get("node"), dict) else {}
    member = data.get("member") if isinstance(data.get("member"), dict) else {}
    title = str(data.get("title") or f"V2EX topic {data.get('id')}")
    lines = [title]
    for key in ("content", "content_rendered"):
        if data.get(key):
            lines.append(str(data.get(key)))
            break
    if node.get("name"):
        lines.append(f"node: {node.get('name')}")
    if member.get("username"):
        lines.append(f"author: {member.get('username')}")
    return RetrievedItem(
        title=title,
        url=data.get("url") or (f"https://www.v2ex.com/t/{data.get('id')}" if data.get("id") else None),
        text=compact_text("\n".join(lines)),
        metadata={"id": data.get("id"), "node": node.get("name"), "author": member.get("username")},
    )


def _reply_item(data: dict) -> RetrievedItem:
    member = data.get("member") if isinstance(data.get("member"), dict) else {}
    title = str(member.get("username") or f"Reply {data.get('id')}")
    return RetrievedItem(
        title=title,
        url=data.get("url"),
        text=compact_text(str(data.get("content") or data.get("content_rendered") or "")),
        metadata={"id": data.get("id"), "author": member.get("username")},
    )
