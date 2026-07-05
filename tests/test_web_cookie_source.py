from __future__ import annotations

import json

from reachkit.runtime.http import HttpResponse
from reachkit.sources.web import WebReader


def test_web_reader_passes_cookie_header_from_file(tmp_path):
    cookie_file = tmp_path / "cookies.json"
    cookie_file.write_text(json.dumps([{"name": "session", "value": "abc123"}]), encoding="utf-8")
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append((url, kwargs))
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "text/plain"},
            body="hello",
        )

    result = WebReader(fetcher=fake_fetch).read("https://example.com", cookie_file=str(cookie_file))

    assert result.items[0].text == "hello"
    assert calls[0][1]["headers"] == {"Cookie": "session=abc123"}


def test_web_reader_passes_cookie_header_from_storage_state(tmp_path):
    storage_state = tmp_path / "storage-state.json"
    storage_state.write_text(json.dumps({"cookies": [{"name": "session", "value": "abc123"}]}), encoding="utf-8")
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append((url, kwargs))
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "text/plain"},
            body="hello",
        )

    result = WebReader(fetcher=fake_fetch).read("https://example.com", storage_state=str(storage_state))

    assert result.items[0].text == "hello"
    assert calls[0][1]["headers"] == {"Cookie": "session=abc123"}
