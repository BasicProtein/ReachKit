from __future__ import annotations

import json

import pytest

from reachkit.core.errors import ConfigError
from reachkit.runtime.http import HttpResponse
from reachkit.sources.xiaohongshu import XiaohongshuApiReader


def test_xiaohongshu_api_reader_requires_credentials(monkeypatch):
    monkeypatch.delenv("XHS_APP_KEY", raising=False)
    monkeypatch.delenv("XHS_APP_SECRET", raising=False)

    with pytest.raises(ConfigError):
        XiaohongshuApiReader(fetcher=lambda url, **kwargs: None).read("/api/open/test")


def test_xiaohongshu_api_reader_sends_signed_headers(monkeypatch):
    monkeypatch.setenv("XHS_APP_KEY", "app-key")
    monkeypatch.setenv("XHS_APP_SECRET", "app-secret")
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append((url, kwargs))
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps({"code": 0, "data": {"title": "Sample note", "body": "Useful public content"}}),
        )

    result = XiaohongshuApiReader(fetcher=fake_fetch, clock=lambda: 1000).read(
        "/api/open/test",
        query={"note_id": "abc"},
    )

    assert result.source == "xiaohongshu"
    assert result.items[0].title == "Sample note"
    assert "Useful public content" in result.items[0].text
    assert calls[0][0] == "https://edith.xiaohongshu.com/api/open/test?note_id=abc"
    assert calls[0][1]["headers"]["app-key"] == "app-key"
    assert calls[0][1]["headers"]["timestamp"] == "1000"
    assert calls[0][1]["headers"]["sign"]
