from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
import os
import time
from urllib.parse import urlencode

from reachkit.core.errors import ConfigError, InputError, ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text

FetchText = Callable[..., HttpResponse]

DEFAULT_BASE_URL = "https://edith.xiaohongshu.com"


class XiaohongshuApiReader:
    name = "xiaohongshu"

    def __init__(
        self,
        fetcher: FetchText | None = None,
        clock: Callable[[], int] | None = None,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self._fetcher = fetcher
        self._clock = clock or (lambda: int(time.time()))
        self._base_url = base_url.rstrip("/")

    def read(self, path: str, query: dict[str, str] | None = None) -> SourceResult:
        if not path.startswith("/"):
            raise InputError("Xiaohongshu API path must start with /")
        app_key = os.environ.get("XHS_APP_KEY")
        app_secret = os.environ.get("XHS_APP_SECRET")
        if not app_key or not app_secret:
            raise ConfigError("XHS_APP_KEY and XHS_APP_SECRET are required")
        active_query = query or {}
        timestamp = str(self._clock())
        sign = _sign_request(path, active_query, app_key=app_key, app_secret=app_secret, timestamp=timestamp)
        headers = {"app-key": app_key, "timestamp": timestamp, "sign": sign}
        url = self._base_url + path
        if active_query:
            url = f"{url}?{urlencode(active_query)}"
        active_fetcher = self._fetcher or fetch_text
        response = active_fetcher(url, headers=headers)
        payload = self._load_json(response)
        item = _payload_to_item(path, payload)
        return SourceResult(self.name, response.url, f"Xiaohongshu API: {path}", response.headers.get("Content-Type"), [item], [])

    def _load_json(self, response: HttpResponse):
        try:
            return json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise ParseError("Xiaohongshu response was not valid JSON") from exc


def _sign_request(path: str, query: dict[str, str], app_key: str, app_secret: str, timestamp: str) -> str:
    params = {**query, "app-key": app_key, "timestamp": timestamp}
    pieces = [f"{key}={params[key]}" for key in sorted(params)]
    raw = path + "?" + "&".join(pieces) + app_secret
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _payload_to_item(path: str, payload) -> RetrievedItem:
    data = payload.get("data") if isinstance(payload, dict) else payload
    title = _find_text(data, ("title", "name", "id")) or f"Xiaohongshu API: {path}"
    text = _payload_text(data)
    metadata = payload if isinstance(payload, dict) else {"data": payload}
    return RetrievedItem(title=title, url=None, text=text, metadata=metadata)


def _payload_text(data) -> str:
    if isinstance(data, dict):
        fields: list[str] = []
        for key in ("title", "name", "body", "content", "desc", "description", "id"):
            value = data.get(key)
            if isinstance(value, (str, int, float)):
                fields.append(str(value))
        if fields:
            return compact_text("\n".join(fields))
    return compact_text(json.dumps(data, ensure_ascii=False, sort_keys=True))


def _find_text(data, keys: tuple[str, ...]) -> str | None:
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if isinstance(value, (str, int, float)) and str(value):
            return str(value)
    return None
