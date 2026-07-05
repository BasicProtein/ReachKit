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


def test_read_facebook_cli(monkeypatch, capsys):
    from reachkit.cli.commands import read

    class Reader:
        def read(self, target):
            assert target == "pg1"
            return _result("facebook", "Page name")

    monkeypatch.setattr(read, "FacebookGraphReader", lambda: Reader())

    exit_code = app.main(["read", "facebook", "pg1"])

    assert exit_code == 0
    assert "Page name" in capsys.readouterr().out


def test_read_instagram_cli(monkeypatch, capsys):
    from reachkit.cli.commands import read

    class Reader:
        def read(self, target):
            assert target == "ig1"
            return _result("instagram", "demo")

    monkeypatch.setattr(read, "InstagramGraphReader", lambda: Reader())

    exit_code = app.main(["read", "instagram", "ig1"])

    assert exit_code == 0
    assert "demo" in capsys.readouterr().out
