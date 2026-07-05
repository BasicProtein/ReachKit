from __future__ import annotations

import os

from reachkit.channels.models import ProviderStatus
from reachkit.channels.providers.common import available, needs_config


def provider_statuses() -> list[ProviderStatus]:
    if os.environ.get("XHS_APP_KEY") and os.environ.get("XHS_APP_SECRET"):
        return [available("open_api", "official_api", "Xiaohongshu open API credentials are configured.")]
    return [
        needs_config(
            "open_api",
            "official_api",
            "Xiaohongshu open API credentials are not configured.",
            "Set XHS_APP_KEY and XHS_APP_SECRET before reading Xiaohongshu API paths.",
        )
    ]
