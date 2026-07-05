from __future__ import annotations

from dataclasses import dataclass
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener

from reachkit.core.errors import FetchError
from reachkit.runtime.limits import DEFAULT_MAX_BYTES, DEFAULT_TIMEOUT_SECONDS

USER_AGENT = "ReachKit/0.1 (+https://local.invalid/reachkit)"


@dataclass(frozen=True)
class HttpResponse:
    url: str
    status: int
    headers: dict[str, str]
    body: str


def fetch_text(
    url: str,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_bytes: int = DEFAULT_MAX_BYTES,
    opener: Any | None = None,
    headers: dict[str, str] | None = None,
) -> HttpResponse:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise FetchError("URL scheme is not allowed")
    if max_bytes < 1:
        raise FetchError("Response size limit must be positive")

    request_headers = {"User-Agent": USER_AGENT}
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    transport = opener or build_opener()

    try:
        with transport.open(request, timeout=timeout) as response:
            status = int(getattr(response, "status", 200))
            if status < 200 or status > 299:
                raise FetchError(f"HTTP request failed with status {status}")
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise FetchError("Response body is too large")
            header_items = dict(response.headers.items())
            charset = response.headers.get_content_charset() or "utf-8"
            body = raw.decode(charset, errors="replace")
            response_url = getattr(response, "url", url)
            return HttpResponse(url=response_url, status=status, headers=header_items, body=body)
    except FetchError:
        raise
    except (HTTPError, URLError, TimeoutError, socket.timeout, OSError) as exc:
        raise FetchError("HTTP request failed") from exc
