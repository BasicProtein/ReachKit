from __future__ import annotations

from collections.abc import Callable
import json
import os
import re
from urllib.parse import urlencode, urlparse

from reachkit.core.errors import ConfigError, InputError, ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text

FetchText = Callable[..., HttpResponse]


def parse_post_id(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        raise InputError("X post id is required")
    if candidate.isdigit():
        return candidate
    parsed = urlparse(candidate)
    parts = [part for part in parsed.path.split("/") if part]
    if "status" in parts:
        index = parts.index("status")
        if index + 1 < len(parts) and parts[index + 1].isdigit():
            return parts[index + 1]
    match = re.search(r"/status/(\d+)", candidate)
    if match:
        return match.group(1)
    raise InputError("X post id could not be found")


def _bearer_token() -> str:
    token = os.environ.get("X_BEARER_TOKEN") or os.environ.get("TWITTER_BEARER_TOKEN")
    if not token:
        raise ConfigError("X_BEARER_TOKEN is required")
    return token


class XPostReader:
    name = "x"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(self, post: str) -> SourceResult:
        post_id = parse_post_id(post)
        query = urlencode(
            {
                "tweet.fields": "author_id,created_at,lang,public_metrics",
                "expansions": "author_id",
                "user.fields": "name,username",
            }
        )
        url = f"https://api.x.com/2/tweets/{post_id}?{query}"
        active_fetcher = self._fetcher or fetch_text
        response = active_fetcher(url, headers={"Authorization": f"Bearer {_bearer_token()}"})
        data = self._load_json(response)
        if not isinstance(data, dict):
            raise ParseError("X response was not an object")
        post_data = data.get("data")
        if not isinstance(post_data, dict):
            raise ParseError("X response did not contain a post")
        text = compact_text(str(post_data.get("text") or ""))
        if not text:
            raise ParseError("X post text was empty")
        author = self._author(data, post_data.get("author_id"))
        title = f"X post {post_id}"
        post_url = f"https://x.com/i/status/{post_id}"
        metadata = {
            "post_id": post_id,
            "author_id": post_data.get("author_id"),
            "username": author.get("username"),
            "name": author.get("name"),
            "created_at": post_data.get("created_at"),
            "lang": post_data.get("lang"),
            "public_metrics": post_data.get("public_metrics"),
        }
        item = RetrievedItem(title=title, url=post_url, text=text, metadata=metadata)
        return SourceResult(self.name, post_url, title, response.headers.get("Content-Type"), [item], [])

    def _load_json(self, response: HttpResponse):
        try:
            return json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise ParseError("X response was not valid JSON") from exc

    def _author(self, data, author_id) -> dict[str, str | None]:
        users = data.get("includes", {}).get("users", []) if isinstance(data.get("includes"), dict) else []
        for user in users:
            if isinstance(user, dict) and user.get("id") == author_id:
                return {"username": user.get("username"), "name": user.get("name")}
        return {"username": None, "name": None}

    def search(self, query: str, limit: int = 10) -> SourceResult:
        return self._tweet_list(
            "https://api.x.com/2/tweets/search/recent?"
            + urlencode({"query": query, "max_results": max(10, min(limit, 100)), "tweet.fields": "author_id,created_at,lang,public_metrics"}),
            f"X search: {query}",
            limit=limit,
        )

    def thread(self, post: str, limit: int = 10) -> SourceResult:
        post_id = parse_post_id(post)
        query = f"conversation_id:{post_id}"
        return self._tweet_list(
            "https://api.x.com/2/tweets/search/recent?"
            + urlencode({"query": query, "max_results": max(10, min(limit, 100)), "tweet.fields": "author_id,created_at,lang,public_metrics"}),
            f"X thread: {post_id}",
            limit=limit,
        )

    def timeline(self, username: str, limit: int = 10) -> SourceResult:
        query = f"from:{username}"
        return self._tweet_list(
            "https://api.x.com/2/tweets/search/recent?"
            + urlencode({"query": query, "max_results": max(10, min(limit, 100)), "tweet.fields": "author_id,created_at,lang,public_metrics"}),
            f"X timeline: {username}",
            limit=limit,
        )

    def _tweet_list(self, url: str, title: str, limit: int) -> SourceResult:
        active_fetcher = self._fetcher or fetch_text
        response = active_fetcher(url, headers={"Authorization": f"Bearer {_bearer_token()}"})
        data = self._load_json(response)
        if not isinstance(data, dict):
            raise ParseError("X response was not an object")
        items: list[RetrievedItem] = []
        for record in list(data.get("data") or [])[: max(1, limit)]:
            if not isinstance(record, dict):
                continue
            post_id = str(record.get("id") or "")
            text = compact_text(str(record.get("text") or ""))
            if not text:
                continue
            item_title = f"X post {post_id}" if post_id else "X post"
            items.append(
                RetrievedItem(
                    title=item_title,
                    url=f"https://x.com/i/status/{post_id}" if post_id else None,
                    text=text,
                    metadata={
                        "post_id": post_id,
                        "author_id": record.get("author_id"),
                        "created_at": record.get("created_at"),
                        "lang": record.get("lang"),
                        "public_metrics": record.get("public_metrics"),
                    },
                )
            )
        return SourceResult(self.name, response.url, title, response.headers.get("Content-Type"), items, [])
