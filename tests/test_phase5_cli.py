from __future__ import annotations

from reachkit.cli import app
from reachkit.core.models import RetrievedItem, SourceResult


def _result(source: str, title: str) -> SourceResult:
    return SourceResult(
        source=source,
        url=f"https://example.com/{source}",
        title=title,
        content_type="application/json",
        items=[RetrievedItem(title=title, url=None, text=f"{title} text", metadata={})],
    )


def test_search_x_cli(monkeypatch, capsys):
    from reachkit.cli.commands import search

    class Reader:
        def search(self, query, limit):
            assert query == "agent"
            assert limit == 2
            return _result("x", "X result")

    monkeypatch.setattr(search, "XPostReader", lambda: Reader())

    exit_code = app.main(["search", "x", "agent", "--limit", "2"])

    assert exit_code == 0
    assert "X result" in capsys.readouterr().out


def test_read_reddit_cli(monkeypatch, capsys):
    from reachkit.cli.commands import read

    class Reader:
        def read(self, target, limit):
            assert target == "https://reddit.test/post"
            assert limit == 3
            return _result("reddit", "Reddit post")

    monkeypatch.setattr(read, "RedditReader", lambda: Reader())

    exit_code = app.main(["read", "reddit", "https://reddit.test/post", "--limit", "3"])

    assert exit_code == 0
    assert "Reddit post" in capsys.readouterr().out


def test_read_linkedin_cli(monkeypatch, capsys):
    from reachkit.cli.commands import read

    class Reader:
        def read(self, target):
            assert target == "https://www.linkedin.com/company/example/"
            return _result("linkedin", "LinkedIn page")

    monkeypatch.setattr(read, "LinkedInPublicReader", lambda: Reader())

    exit_code = app.main(["read", "linkedin", "https://www.linkedin.com/company/example/"])

    assert exit_code == 0
    assert "LinkedIn page" in capsys.readouterr().out


def test_read_xueqiu_cli(monkeypatch, capsys):
    from reachkit.cli.commands import read

    class Reader:
        def read(self, target):
            assert target == "SH600000"
            return _result("xueqiu", "Demo Bank")

    monkeypatch.setattr(read, "XueqiuReader", lambda: Reader())

    exit_code = app.main(["read", "xueqiu", "SH600000"])

    assert exit_code == 0
    assert "Demo Bank" in capsys.readouterr().out
