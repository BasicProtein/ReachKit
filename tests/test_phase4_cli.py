from __future__ import annotations

import json

from reachkit.cli import app
from reachkit.core.models import RetrievedItem, SourceResult


def _result(source: str, title: str) -> SourceResult:
    return SourceResult(
        source=source,
        url=f"https://example.com/{source}",
        title=title,
        content_type="application/json",
        items=[RetrievedItem(title=title, url=f"https://example.com/{source}", text=f"{title} text", metadata={})],
    )


def test_read_github_issue_cli(monkeypatch, capsys):
    from reachkit.cli.commands import read

    class Reader:
        def read_issue(self, repo, number):
            assert repo == "reachkit/demo"
            assert number == 7
            return _result("github", "Issue title")

    monkeypatch.setattr(read, "GitHubReader", lambda: Reader())

    exit_code = app.main(["read", "github", "reachkit/demo", "--issue", "7", "--format", "json"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["title"] == "Issue title"


def test_search_youtube_cli(monkeypatch, capsys):
    from reachkit.cli.commands import search

    class Reader:
        def search(self, query, limit):
            assert query == "agent tools"
            assert limit == 2
            return _result("youtube", "YouTube result")

    monkeypatch.setattr(search, "YouTubeSearchReader", lambda: Reader())

    exit_code = app.main(["search", "youtube", "agent tools", "--limit", "2"])

    assert exit_code == 0
    assert "YouTube result" in capsys.readouterr().out


def test_search_bilibili_cli(monkeypatch, capsys):
    from reachkit.cli.commands import search

    class Reader:
        def search(self, query, limit):
            assert query == "demo"
            assert limit == 3
            return _result("bilibili", "Bilibili result")

    monkeypatch.setattr(search, "BilibiliVideoReader", lambda: Reader())

    exit_code = app.main(["search", "bilibili", "demo", "--limit", "3"])

    assert exit_code == 0
    assert "Bilibili result" in capsys.readouterr().out


def test_read_v2ex_cli(monkeypatch, capsys):
    from reachkit.cli.commands import read

    class Reader:
        def read(self, target, limit):
            assert target == "hot"
            assert limit == 1
            return _result("v2ex", "Hot topic")

    monkeypatch.setattr(read, "V2EXReader", lambda: Reader())

    exit_code = app.main(["read", "v2ex", "hot", "--limit", "1"])

    assert exit_code == 0
    assert "Hot topic" in capsys.readouterr().out


def test_read_podcast_cli(monkeypatch, capsys):
    from reachkit.cli.commands import read

    class Reader:
        def read(self, url, limit):
            assert url == "https://example.com/feed.xml"
            assert limit == 2
            return _result("podcast", "Episode one")

    monkeypatch.setattr(read, "PodcastReader", lambda: Reader())

    exit_code = app.main(["read", "podcast", "https://example.com/feed.xml", "--limit", "2"])

    assert exit_code == 0
    assert "Episode one" in capsys.readouterr().out
