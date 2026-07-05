from __future__ import annotations

import json

from reachkit.cli import app
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.runtime.http import HttpResponse
from reachkit.sources.v2ex import V2EXReader
from reachkit.sources.web import WebSearchReader
from reachkit.sources.youtube import YouTubeMetadataReader


def _json_response(url: str, payload) -> HttpResponse:
    return HttpResponse(url=url, status=200, headers={"Content-Type": "application/json"}, body=json.dumps(payload))


def _result(source: str, title: str) -> SourceResult:
    return SourceResult(
        source=source,
        url=f"https://example.com/{source}",
        title=title,
        content_type="application/json",
        items=[RetrievedItem(title=title, url=None, text=f"{title} text", metadata={})],
    )


def test_web_search_reader_maps_json_results():
    def fake_fetch(url, **kwargs):
        return _json_response(
            url,
            {
                "items": [
                    {
                        "title": "Example result",
                        "url": "https://example.com",
                        "snippet": "Short result text",
                    }
                ]
            },
        )

    result = WebSearchReader(fetcher=fake_fetch, endpoint="https://search.example/api").search("agent tools", limit=1)

    assert result.source == "web"
    assert result.items[0].title == "Example result"
    assert result.items[0].url == "https://example.com"
    assert result.items[0].text == "Short result text"


def test_youtube_metadata_reader_maps_video_record():
    def fake_fetch(url, **kwargs):
        return _json_response(
            url,
            {
                "items": [
                    {
                        "id": "abc123",
                        "snippet": {
                            "title": "Video title",
                            "description": "Video text",
                            "channelTitle": "Channel",
                            "publishedAt": "2026-01-01T00:00:00Z",
                        },
                        "contentDetails": {"duration": "PT1M"},
                        "statistics": {"viewCount": "12"},
                    }
                ]
            },
        )

    result = YouTubeMetadataReader(fetcher=fake_fetch, api_key="key").read("abc123")

    assert result.items[0].title == "Video title"
    assert result.items[0].metadata["duration"] == "PT1M"
    assert result.items[0].metadata["views"] == "12"


def test_v2ex_topic_includes_replies_when_requested():
    def fake_fetch(url, **kwargs):
        if "replies/show" in url:
            return _json_response(
                url,
                [
                    {
                        "id": 501,
                        "content": "Reply text",
                        "member": {"username": "bob"},
                        "url": "https://www.v2ex.com/t/101#reply501",
                    }
                ],
            )
        return _json_response(
            url,
            [
                {
                    "id": 101,
                    "title": "Topic title",
                    "content": "Topic body",
                    "url": "https://www.v2ex.com/t/101",
                    "node": {"name": "python"},
                    "member": {"username": "alice"},
                }
            ],
        )

    result = V2EXReader(fetcher=fake_fetch).topic(101, include_replies=True, limit=3)

    assert [item.title for item in result.items] == ["Topic title", "bob"]
    assert result.items[1].text == "Reply text"


def test_search_web_cli_uses_reader(monkeypatch, capsys):
    from reachkit.cli.commands import search

    class Reader:
        def search(self, query, limit):
            assert query == "agent tools"
            assert limit == 2
            return _result("web", "Web result")

    monkeypatch.setattr(search, "WebSearchReader", lambda: Reader())

    exit_code = app.main(["search", "web", "agent tools", "--limit", "2"])

    assert exit_code == 0
    assert "Web result" in capsys.readouterr().out


def test_read_youtube_metadata_cli(monkeypatch, capsys):
    from reachkit.cli.commands import read

    class Reader:
        def read(self, video):
            assert video == "abc123"
            return _result("youtube", "Video title")

    monkeypatch.setattr(read, "YouTubeMetadataReader", lambda: Reader())

    exit_code = app.main(["read", "youtube", "abc123", "--metadata"])

    assert exit_code == 0
    assert "Video title" in capsys.readouterr().out


def test_read_xueqiu_hot_cli(monkeypatch, capsys):
    from reachkit.cli.commands import read

    class Reader:
        def hot(self, limit):
            assert limit == 2
            return _result("xueqiu", "Hot stock")

    monkeypatch.setattr(read, "XueqiuReader", lambda: Reader())

    exit_code = app.main(["read", "xueqiu", "hot", "--limit", "2"])

    assert exit_code == 0
    assert "Hot stock" in capsys.readouterr().out
