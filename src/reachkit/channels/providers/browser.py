from __future__ import annotations

from reachkit.channels.models import ProviderStatus
from reachkit.channels.providers.common import available, missing_dependency
from reachkit.sources import browser as browser_source


def provider_statuses() -> list[ProviderStatus]:
    if browser_source.sync_playwright is None:
        return [
            missing_dependency(
                "playwright_browser",
                "explicit_browser_state",
                "Browser rendering extra is not installed.",
                "Install reachkit[browser] and run playwright install chromium.",
            )
        ]
    return [available("playwright_browser", "explicit_browser_state", "Browser rendering extra is installed.")]
