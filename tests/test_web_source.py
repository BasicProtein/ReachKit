import pytest

from reachkit.core.errors import ParseError
from reachkit.runtime.http import HttpResponse
from reachkit.sources import web
from reachkit.sources.web import WebReader


def test_web_reader_parses_html(monkeypatch):
    def fake_fetch(url, **kwargs):
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            body="<title>Example</title><h1>Hello</h1><p>World</p>",
        )

    monkeypatch.setattr(web, "fetch_text", fake_fetch)

    result = WebReader().read(url="https://example.com", max_chars=100)

    assert result.source == "web"
    assert result.title == "Example"
    assert result.content_type == "text/html; charset=utf-8"
    assert result.items[0].text == "Hello World"


def test_web_reader_compacts_plain_text(monkeypatch):
    def fake_fetch(url, **kwargs):
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "text/plain"},
            body=" Alpha\n\nBeta ",
        )

    monkeypatch.setattr(web, "fetch_text", fake_fetch)

    result = WebReader().read(url="https://example.com/text")

    assert result.title is None
    assert result.items[0].text == "Alpha Beta"
    assert result.warnings == []


def test_web_reader_warns_for_other_text_types(monkeypatch):
    def fake_fetch(url, **kwargs):
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "text/csv"},
            body="a,b\n1,2",
        )

    monkeypatch.setattr(web, "fetch_text", fake_fetch)

    result = WebReader().read(url="https://example.com/data.csv")

    assert result.warnings == ["non_html_text"]
    assert result.items[0].text == "a,b 1,2"


def test_web_reader_rejects_binary_content(monkeypatch):
    def fake_fetch(url, **kwargs):
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "application/pdf"},
            body="%PDF",
        )

    monkeypatch.setattr(web, "fetch_text", fake_fetch)

    with pytest.raises(ParseError):
        WebReader().read(url="https://example.com/file.pdf")
