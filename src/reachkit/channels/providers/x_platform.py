from __future__ import annotations

import os

from reachkit.channels.models import ProviderStatus
from reachkit.channels.providers.common import available, needs_config


def provider_statuses() -> list[ProviderStatus]:
    if os.environ.get("X_BEARER_TOKEN") or os.environ.get("TWITTER_BEARER_TOKEN"):
        return [available("official_api", "official_api", "X API bearer token is configured.")]
    return [
        needs_config(
            "official_api",
            "official_api",
            "X API bearer token is not configured.",
            "Set X_BEARER_TOKEN or TWITTER_BEARER_TOKEN before reading X posts.",
        )
    ]
