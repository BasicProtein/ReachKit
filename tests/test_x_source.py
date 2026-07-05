from __future__ import annotations

import json

import pytest

from reachkit.core.errors import ConfigError, ParseError
from reachkit.runtime.http import HttpResponse
from reachkit.sources.x_platform import XPostReader, parse_post_id


def test_parse_post_id_accepts_urls_and_ids():
    assert parse_post_id("https://x.com/example/status/1234567890") == "1234567890"
    assert parse_post_id("https://twitter.com/example/status/1234567890") == "1234567890"
    assert parse_post_id("1234567890") == "1234567890"


def test_x_post_reader_requires_bearer_token(monkeypatch):
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_BEARER_TOKEN", raising=False)

    with pytest.raises(ConfigError):
        XPostReader(fetcher=lambda url, **kwargs: None).read("1234567890")


def test_x_post_reader_maps_api_payload(monkeypatch):
    monkeypatch.setenv("X_BEARER_TOKEN", "token-123")
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append((url, kwargs))
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(
                {
                    "data": {
                        "id": "1234567890",
                        "text": "Agent retrieval works.",
                        "author_id": "42",
                        "created_at": "2026-07-05T10:00:00Z",
                    },
                    "includes": {"users": [{"id": "42", "username": "reachkit", "name": "ReachKit"}]},
                }
            ),
        )

    result = XPostReader(fetcher=fake_fetch).read("1234567890")

    assert result.source == "x"
    assert result.items[0].text == "Agent retrieval works."
    assert result.items[0].metadata["username"] == "reachkit"
    assert calls[0][1]["headers"]["Authorization"] == "Bearer token-123"


def test_x_post_reader_rejects_non_object_payload(monkeypatch):
    monkeypatch.setenv("X_BEARER_TOKEN", "token-123")

    def fake_fetch(url, **kwargs):
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(["not", "an", "object"]),
        )

    with pytest.raises(ParseError):
        XPostReader(fetcher=fake_fetch).read("1234567890")
