from __future__ import annotations

import pytest

from reachkit.core.errors import ConfigError, InputError
from reachkit.sources.browser import BrowserReader, BrowserSnapshot


def test_browser_reader_requires_playwright_when_no_runner(monkeypatch):
    monkeypatch.setattr("reachkit.sources.browser.sync_playwright", None)

    with pytest.raises(ConfigError):
        BrowserReader().read("https://example.com")


def test_browser_reader_maps_runner_snapshot():
    calls = []

    def fake_runner(url, **kwargs):
        calls.append((url, kwargs))
        return BrowserSnapshot(
            url="https://example.com/final",
            title="Example",
            text="Example Domain\nThis domain is for examples.",
        )

    result = BrowserReader(runner=fake_runner).read(
        "https://example.com",
        storage_state="storage-state.json",
        wait_until="networkidle",
        max_chars=20,
    )

    assert result.source == "browser"
    assert result.url == "https://example.com/final"
    assert result.title == "Example"
    assert result.items[0].text == "Example Domain\nTh..."
    assert calls[0][1]["storage_state"] == "storage-state.json"
    assert calls[0][1]["wait_until"] == "networkidle"


def test_browser_reader_rejects_unknown_wait_until():
    with pytest.raises(InputError):
        BrowserReader(runner=lambda url, **kwargs: BrowserSnapshot(url=url, title=None, text="body")).read(
            "https://example.com",
            wait_until="forever",
        )
