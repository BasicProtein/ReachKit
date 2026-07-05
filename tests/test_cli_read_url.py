import json

from reachkit.cli import app
from reachkit.core.models import RetrievedItem, SourceResult


class StubWebReader:
    def __init__(self):
        self.calls = []

    def read(self, **kwargs):
        self.calls.append(kwargs)
        return SourceResult(
            source="web",
            url=kwargs["url"],
            title="Example",
            content_type="text/html",
            items=[
                RetrievedItem(
                    title="Example",
                    url=kwargs["url"],
                    text="Hello World",
                )
            ],
        )


def test_read_url_outputs_text(monkeypatch, capsys):
    reader = StubWebReader()
    from reachkit.cli.commands import read

    monkeypatch.setattr(read, "WebReader", lambda: reader)

    exit_code = app.main(["read", "url", "https://example.com"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Hello World" in captured.out
    assert reader.calls == [{"url": "https://example.com", "max_chars": 12000}]


def test_read_url_outputs_json(monkeypatch, capsys):
    from reachkit.cli.commands import read

    monkeypatch.setattr(read, "WebReader", lambda: StubWebReader())

    exit_code = app.main(["read", "url", "https://example.com", "--format", "json", "--max-chars", "25"])

    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["source"] == "web"
    assert payload["items"][0]["text"] == "Hello World"


def test_read_url_rejects_too_large_max_chars(capsys):
    exit_code = app.main(["read", "url", "https://example.com", "--max-chars", "100001"])

    assert exit_code == 2
