from __future__ import annotations

import os

from reachkit.channels.models import ProviderStatus
from reachkit.channels.providers.common import available, needs_config


def provider_statuses() -> list[ProviderStatus]:
    statuses = [available("http_reader", "public", "Built-in URL reader is available.")]
    if os.environ.get("REACHKIT_WEB_SEARCH_URL"):
        statuses.append(available("search_endpoint", "official_api", "Configured web search endpoint is available."))
    else:
        statuses.append(
            needs_config(
                "search_endpoint",
                "official_api",
                "Web search endpoint is not configured.",
                "Set REACHKIT_WEB_SEARCH_URL to a JSON search endpoint.",
            )
        )
    return statuses
