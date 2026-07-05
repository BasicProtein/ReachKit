from __future__ import annotations

import json
from urllib.parse import unquote

import pytest

from reachkit.core.errors import ConfigError
from reachkit.runtime.http import HttpResponse
from reachkit.sources.linkedin import LinkedInPublicReader
from reachkit.sources.reddit import RedditReader
from reachkit.sources.x_platform import XPostReader
from reachkit.sources.xiaohongshu import XiaohongshuApiReader
from reachkit.sources.xueqiu import XueqiuReader


def _json_response(url: str, payload) -> HttpResponse:
    return HttpResponse(url=url, status=200, headers={"Content-Type": "application/json"}, body=json.dumps(payload))


def test_x_reader_search_thread_and_timeline_use_bearer_token(monkeypatch):
    monkeypatch.setenv("X_BEARER_TOKEN", "token")
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append((url, kwargs))
        decoded_url = unquote(url)
        if "conversation_id:1" in decoded_url:
            return _json_response(url, {"data": [{"id": "2", "text": "Thread reply", "author_id": "u2"}]})
        if "from:alice" in decoded_url:
            return _json_response(url, {"data": [{"id": "3", "text": "Timeline post", "author_id": "u3"}]})
        return _json_response(url, {"data": [{"id": "1", "text": "Search post", "author_id": "u1"}]})

    reader = XPostReader(fetcher=fake_fetch)

    search = reader.search("agent", limit=1)
    thread = reader.thread("1", limit=1)
    timeline = reader.timeline("alice", limit=1)

    assert search.items[0].title == "X post 1"
    assert thread.items[0].metadata["post_id"] == "2"
    assert timeline.items[0].text == "Timeline post"
    assert all(call[1]["headers"]["Authorization"] == "Bearer token" for call in calls)


def test_x_reader_search_requires_token(monkeypatch):
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_BEARER_TOKEN", raising=False)

    with pytest.raises(ConfigError):
        XPostReader(fetcher=lambda url, **kwargs: _json_response(url, {})).search("agent")


def test_xiaohongshu_reader_search_note_and_comments(monkeypatch):
    monkeypatch.setenv("XHS_APP_KEY", "key")
    monkeypatch.setenv("XHS_APP_SECRET", "secret")
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append(url)
        return _json_response(url, {"data": {"title": "Note title", "content": "Note text", "id": "n1"}})

    reader = XiaohongshuApiReader(fetcher=fake_fetch, clock=lambda: 100)

    search = reader.search("coffee")
    note = reader.note("n1")
    comments = reader.comments("n1")

    assert search.items[0].title == "Note title"
    assert note.items[0].metadata["data"]["id"] == "n1"
    assert comments.items[0].text.startswith("Note title")
    assert any("/note/search" in call for call in calls)
    assert any("/note/detail" in call for call in calls)
    assert any("/note/comments" in call for call in calls)


def test_reddit_reader_search_post_and_comments():
    def fake_fetch(url, **kwargs):
        if "/search.json" in url:
            return _json_response(
                url,
                {"data": {"children": [{"data": {"title": "Reddit post", "permalink": "/r/demo/comments/abc/post", "selftext": "Body"}}]}},
            )
        return _json_response(
            url,
            [
                {"data": {"children": [{"data": {"title": "Reddit post", "selftext": "Body", "permalink": "/r/demo/comments/abc/post"}}]}},
                {"data": {"children": [{"data": {"body": "Comment body", "permalink": "/r/demo/comments/abc/post/c1"}}]}},
            ],
        )

    reader = RedditReader(fetcher=fake_fetch)

    search = reader.search("agent", limit=1)
    post = reader.read("https://www.reddit.com/r/demo/comments/abc/post/")

    assert search.items[0].title == "Reddit post"
    assert post.items[0].title == "Reddit post"
    assert post.items[1].text == "Comment body"


def test_linkedin_public_reader_uses_web_page_text():
    html = "<html><head><title>Company | LinkedIn</title></head><body><main>Company profile text</main></body></html>"

    def fake_fetch(url, **kwargs):
        return HttpResponse(url=url, status=200, headers={"Content-Type": "text/html"}, body=html)

    result = LinkedInPublicReader(fetcher=fake_fetch).read("https://www.linkedin.com/company/example/")

    assert result.title == "Company | LinkedIn"
    assert "Company profile text" in result.items[0].text


def test_xueqiu_reader_quote_search_and_hot():
    def fake_fetch(url, **kwargs):
        if "/stock/quote.json" in url:
            return _json_response(url, {"data": [{"symbol": "SH600000", "name": "Demo Bank", "current": 10.5}]})
        if "/stock/search.json" in url:
            return _json_response(url, {"data": [{"code": "SH600000", "name": "Demo Bank"}]})
        return _json_response(url, {"data": {"items": [{"title": "Hot stock", "symbol": "SH600000"}]}})

    reader = XueqiuReader(fetcher=fake_fetch)

    quote = reader.quote("SH600000")
    search = reader.search("demo")
    hot = reader.hot()

    assert quote.items[0].metadata["symbol"] == "SH600000"
    assert search.items[0].title == "Demo Bank"
    assert hot.items[0].title == "Hot stock"
