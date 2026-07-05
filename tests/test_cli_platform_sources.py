from __future__ import annotations

import json

from reachkit.cli import app
from reachkit.core.models import RetrievedItem, SourceResult


def test_read_url_accepts_cookie_file(monkeypatch, tmp_path, capsys):
    cookie_file = tmp_path / "cookies.json"
    cookie_file.write_text('[{"name":"session","value":"abc123"}]', encoding="utf-8")
    calls = []

    class StubReader:
        def read(self, **kwargs):
            calls.append(kwargs)
            return SourceResult(
                source="web",
                url=kwargs["url"],
                title=None,
                content_type="text/plain",
                items=[RetrievedItem(title=None, url=kwargs["url"], text="hello", metadata={})],
                warnings=[],
            )

    monkeypatch.setattr("reachkit.cli.commands.read.WebReader", StubReader)

    exit_code = app.main(["read", "url", "https://example.com", "--cookie-file", str(cookie_file), "--format", "json"])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)["items"][0]["text"] == "hello"
    assert calls[0]["cookie_file"] == str(cookie_file)
    assert calls[0]["storage_state"] is None


def test_read_url_accepts_storage_state(monkeypatch, tmp_path, capsys):
    storage_state = tmp_path / "storage-state.json"
    storage_state.write_text('{"cookies":[{"name":"session","value":"abc123"}]}', encoding="utf-8")
    calls = []

    class StubReader:
        def read(self, **kwargs):
            calls.append(kwargs)
            return SourceResult(
                source="web",
                url=kwargs["url"],
                title=None,
                content_type="text/plain",
                items=[RetrievedItem(title=None, url=kwargs["url"], text="hello", metadata={})],
                warnings=[],
            )

    monkeypatch.setattr("reachkit.cli.commands.read.WebReader", StubReader)

    exit_code = app.main(["read", "url", "https://example.com", "--storage-state", str(storage_state), "--format", "json"])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)["items"][0]["text"] == "hello"
    assert calls[0]["storage_state"] == str(storage_state)
    assert calls[0]["cookie_file"] is None


def test_read_youtube_outputs_json(monkeypatch, capsys):
    class StubReader:
        def read(self, **kwargs):
            return SourceResult(
                source="youtube",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                title="YouTube transcript: dQw4w9WgXcQ",
                content_type="text/xml",
                items=[
                    RetrievedItem(
                        title="Transcript",
                        url="https://youtu.be/dQw4w9WgXcQ",
                        text="Hello world",
                        metadata={},
                    )
                ],
                warnings=[],
            )

    monkeypatch.setattr("reachkit.cli.commands.read.YouTubeTranscriptReader", StubReader)

    exit_code = app.main(["read", "youtube", "dQw4w9WgXcQ", "--lang", "en", "--format", "json"])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["source"] == "youtube"
    assert output["items"][0]["text"] == "Hello world"


def test_read_x_outputs_text(monkeypatch, capsys):
    class StubReader:
        def read(self, post):
            return SourceResult(
                source="x",
                url="https://x.com/i/status/1234567890",
                title="X post 1234567890",
                content_type="application/json",
                items=[
                    RetrievedItem(
                        title="X post 1234567890",
                        url="https://x.com/i/status/1234567890",
                        text="Agent retrieval works.",
                        metadata={},
                    )
                ],
                warnings=[],
            )

    monkeypatch.setattr("reachkit.cli.commands.read.XPostReader", StubReader)

    exit_code = app.main(["read", "x", "1234567890"])

    assert exit_code == 0
    assert "Agent retrieval works." in capsys.readouterr().out


def test_read_bilibili_outputs_text(monkeypatch, capsys):
    class StubReader:
        def read(self, video):
            return SourceResult(
                source="bilibili",
                url="https://www.bilibili.com/video/BV1xx411c7mD",
                title="Demo video",
                content_type="application/json",
                items=[
                    RetrievedItem(
                        title="Demo video",
                        url="https://www.bilibili.com/video/BV1xx411c7mD",
                        text="Demo video\nA useful public video",
                        metadata={},
                    )
                ],
                warnings=[],
            )

    monkeypatch.setattr("reachkit.cli.commands.read.BilibiliVideoReader", StubReader)

    exit_code = app.main(["read", "bilibili", "BV1xx411c7mD"])

    assert exit_code == 0
    assert "A useful public video" in capsys.readouterr().out


def test_read_browser_outputs_text(monkeypatch, capsys):
    calls = []

    class StubReader:
        def read(self, **kwargs):
            calls.append(kwargs)
            return SourceResult(
                source="browser",
                url=kwargs["url"],
                title="Example",
                content_type="text/html",
                items=[RetrievedItem(title="Example", url=kwargs["url"], text="Rendered text", metadata={})],
                warnings=[],
            )

    monkeypatch.setattr("reachkit.cli.commands.read.BrowserReader", StubReader)

    exit_code = app.main(["read", "browser", "https://example.com", "--storage-state", "storage-state.json"])

    assert exit_code == 0
    assert "Rendered text" in capsys.readouterr().out
    assert calls[0]["storage_state"] == "storage-state.json"
