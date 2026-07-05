from pathlib import Path

import pytest

from reachkit.core.errors import ParseError
from reachkit.runtime.http import HttpResponse
from reachkit.sources.rss import RssReader

FIXTURES = Path(__file__).parent / "fixtures"


def _response(body: str) -> HttpResponse:
    return HttpResponse(
        url="https://example.com/feed.xml",
        status=200,
        headers={"Content-Type": "application/xml"},
        body=body,
    )


def test_rss_reader_parses_rss_items():
    body = (FIXTURES / "sample-rss.xml").read_text(encoding="utf-8")
    reader = RssReader(fetcher=lambda url: _response(body))

    result = reader.read("https://example.com/feed.xml", limit=1)

    assert result.source == "rss"
    assert result.title == "ReachKit Notes"
    assert len(result.items) == 1
    assert result.items[0].title == "First Note"
    assert result.items[0].metadata["kind"] == "rss"
    assert result.items[0].metadata["published"] == "Mon, 01 Jan 2024 00:00:00 GMT"


def test_rss_reader_parses_atom_entries():
    body = (FIXTURES / "sample-atom.xml").read_text(encoding="utf-8")
    reader = RssReader(fetcher=lambda url: _response(body))

    result = reader.read("https://example.com/atom.xml")

    assert result.title == "ReachKit Updates"
    assert result.items[0].url == "https://example.com/atom-item"
    assert result.items[0].text == "Atom summary text."
    assert result.items[0].metadata["kind"] == "atom"


def test_rss_reader_returns_warning_for_empty_feed():
    body = "<rss><channel><title>Empty</title></channel></rss>"
    reader = RssReader(fetcher=lambda url: _response(body))

    result = reader.read("https://example.com/feed.xml")

    assert result.items == []
    assert result.warnings == ["empty_feed"]


def test_rss_reader_rejects_invalid_xml():
    reader = RssReader(fetcher=lambda url: _response("<rss>"))

    with pytest.raises(ParseError):
        reader.read("https://example.com/feed.xml")
