import json

from reachkit.cli import app
from reachkit.core.models import RetrievedItem, SourceResult


class StubRssReader:
    def __init__(self):
        self.calls = []

    def read(self, **kwargs):
        self.calls.append(kwargs)
        return SourceResult(
            source="rss",
            url=kwargs["url"],
            title="Feed",
            content_type="application/xml",
            items=[
                RetrievedItem(
                    title="Entry",
                    url="https://example.com/entry",
                    text="Entry text",
                    metadata={"kind": "rss"},
                )
            ],
        )


def test_read_rss_outputs_json(monkeypatch, capsys):
    reader = StubRssReader()
    from reachkit.cli.commands import read

    monkeypatch.setattr(read, "RssReader", lambda: reader)

    exit_code = app.main(["read", "rss", "https://example.com/feed.xml", "--format", "json", "--limit", "5"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out)["items"][0]["metadata"]["kind"] == "rss"
    assert reader.calls == [{"url": "https://example.com/feed.xml", "limit": 5}]


def test_read_rss_caps_limit(monkeypatch, capsys):
    reader = StubRssReader()
    from reachkit.cli.commands import read

    monkeypatch.setattr(read, "RssReader", lambda: reader)

    exit_code = app.main(["read", "rss", "https://example.com/feed.xml", "--limit", "99"])

    assert exit_code == 0
    assert reader.calls[0]["limit"] == 50
