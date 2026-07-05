from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from reachkit.core.errors import ConfigError, InputError, ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import truncate_text

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - depends on optional extra
    sync_playwright = None  # type: ignore[assignment]


@dataclass(frozen=True)
class BrowserSnapshot:
    url: str
    title: str | None
    text: str


BrowserRunner = Callable[..., BrowserSnapshot]
WAIT_UNTIL_VALUES = {"commit", "domcontentloaded", "load", "networkidle"}


class BrowserReader:
    name = "browser"

    def __init__(self, runner: BrowserRunner | None = None) -> None:
        self._runner = runner

    def read(
        self,
        url: str,
        storage_state: str | None = None,
        wait_until: str = "load",
        max_chars: int | None = None,
    ) -> SourceResult:
        if wait_until not in WAIT_UNTIL_VALUES:
            raise InputError("Browser wait_until value is not valid")
        runner = self._runner or _run_browser
        snapshot = runner(url, storage_state=storage_state, wait_until=wait_until)
        text = truncate_text(snapshot.text.strip(), max_chars=max_chars)
        if not text:
            raise ParseError("Browser page text was empty")
        item = RetrievedItem(
            title=snapshot.title,
            url=snapshot.url,
            text=text,
            metadata={"rendered": True, "storage_state": bool(storage_state), "wait_until": wait_until},
        )
        return SourceResult(self.name, snapshot.url, snapshot.title, "text/html", [item], [])


def _run_browser(url: str, storage_state: str | None = None, wait_until: str = "load") -> BrowserSnapshot:
    if sync_playwright is None:
        raise ConfigError("Install reachkit[browser] to use browser reads")
    context_options: dict[str, Any] = {}
    if storage_state:
        context_options["storage_state"] = storage_state
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            context = browser.new_context(**context_options)
            page = context.new_page()
            page.goto(url, wait_until=wait_until, timeout=30000)
            title = page.title() or None
            text = page.locator("body").inner_text(timeout=10000)
            return BrowserSnapshot(url=page.url, title=title, text=text)
        finally:
            browser.close()
