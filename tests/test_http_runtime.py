from __future__ import annotations

from io import BytesIO
import urllib.error

import pytest

from reachkit.core.errors import FetchError
from reachkit.runtime.http import USER_AGENT, HttpResponse, fetch_text


class FakeHeaders:
    def __init__(self, content_type: str | None = None):
        self._content_type = content_type

    def get_content_charset(self):
        if self._content_type and "charset=" in self._content_type:
            return self._content_type.split("charset=", 1)[1]
        return None

    def items(self):
        if self._content_type:
            return [("Content-Type", self._content_type)]
        return []


class FakeResponse:
    def __init__(self, body: bytes, url: str = "https://example.com", status: int = 200, content_type: str | None = "text/plain; charset=utf-8"):
        self._stream = BytesIO(body)
        self.url = url
        self.status = status
        self.headers = FakeHeaders(content_type)

    def read(self, size: int = -1):
        return self._stream.read(size)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeOpener:
    def __init__(self, response):
        self.response = response
        self.request = None
        self.timeout = None

    def open(self, request, timeout=0):
        self.request = request
        self.timeout = timeout
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response


def test_fetch_text_decodes_successful_response():
    opener = FakeOpener(FakeResponse("café".encode("latin-1"), content_type="text/plain; charset=latin-1"))

    response = fetch_text("https://example.com", opener=opener)

    assert isinstance(response, HttpResponse)
    assert response.body == "café"
    assert response.status == 200
    assert response.headers["Content-Type"] == "text/plain; charset=latin-1"
    assert opener.request.headers["User-agent"] == USER_AGENT
    assert opener.timeout == 15.0


def test_fetch_text_rejects_disallowed_scheme():
    with pytest.raises(FetchError):
        fetch_text("file:///tmp/content.txt", opener=FakeOpener(FakeResponse(b"x")))


def test_fetch_text_rejects_large_body():
    opener = FakeOpener(FakeResponse(b"abcdef"))

    with pytest.raises(FetchError):
        fetch_text("https://example.com", max_bytes=5, opener=opener)


def test_fetch_text_wraps_http_error():
    error = urllib.error.HTTPError("https://example.com", 404, "Missing", {}, None)

    with pytest.raises(FetchError):
        fetch_text("https://example.com", opener=FakeOpener(error))
