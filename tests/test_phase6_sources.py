from __future__ import annotations

import json

import pytest

from reachkit.core.errors import ConfigError
from reachkit.runtime.http import HttpResponse
from reachkit.sources.facebook import FacebookGraphReader
from reachkit.sources.instagram import InstagramGraphReader


def _json_response(url: str, payload) -> HttpResponse:
    return HttpResponse(url=url, status=200, headers={"Content-Type": "application/json"}, body=json.dumps(payload))


def test_facebook_graph_reader_requires_explicit_token(monkeypatch):
    monkeypatch.delenv("FACEBOOK_ACCESS_TOKEN", raising=False)

    with pytest.raises(ConfigError):
        FacebookGraphReader(fetcher=lambda url, **kwargs: _json_response(url, {})).page("me")


def test_facebook_graph_reader_reads_page_feed_and_search(monkeypatch):
    monkeypatch.setenv("FACEBOOK_ACCESS_TOKEN", "token")
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append((url, kwargs))
        if "/feed" in url:
            return _json_response(url, {"data": [{"id": "p1", "message": "Feed post", "permalink_url": "https://facebook.test/p1"}]})
        if "/search" in url:
            return _json_response(url, {"data": [{"id": "pg1", "name": "Page result", "link": "https://facebook.test/page"}]})
        return _json_response(url, {"id": "pg1", "name": "Page name", "about": "About text", "link": "https://facebook.test/page"})

    reader = FacebookGraphReader(fetcher=fake_fetch)

    page = reader.page("pg1")
    feed = reader.feed("pg1", limit=1)
    search = reader.search("demo", limit=1)

    assert page.items[0].title == "Page name"
    assert feed.items[0].text == "Feed post"
    assert search.items[0].title == "Page result"
    assert all("access_token=token" in call[0] for call in calls)


def test_instagram_graph_reader_requires_explicit_token(monkeypatch):
    monkeypatch.delenv("INSTAGRAM_ACCESS_TOKEN", raising=False)

    with pytest.raises(ConfigError):
        InstagramGraphReader(fetcher=lambda url, **kwargs: _json_response(url, {})).profile("me")


def test_instagram_graph_reader_reads_profile_media_and_search(monkeypatch):
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "token")
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append(url)
        if "/media" in url:
            return _json_response(url, {"data": [{"id": "m1", "caption": "Caption text", "permalink": "https://instagram.test/p/m1"}]})
        if "ig_hashtag_search" in url:
            return _json_response(url, {"data": [{"id": "h1", "name": "demo"}]})
        return _json_response(url, {"id": "ig1", "username": "demo", "name": "Demo User"})

    reader = InstagramGraphReader(fetcher=fake_fetch)

    profile = reader.profile("ig1")
    media = reader.media("ig1", limit=1)
    search = reader.search("demo", user_id="ig1")

    assert profile.items[0].title == "demo"
    assert media.items[0].text == "Caption text"
    assert search.items[0].title == "demo"
    assert all("access_token=token" in call for call in calls)
