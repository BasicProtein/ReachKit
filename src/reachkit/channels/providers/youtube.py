from __future__ import annotations

import os

from reachkit.channels.models import ProviderStatus
from reachkit.channels.providers.common import available, needs_config


def provider_statuses() -> list[ProviderStatus]:
    statuses = [available("timed_text", "public", "Public timed text lookup is available when a video exposes captions.")]
    if os.environ.get("YOUTUBE_API_KEY"):
        statuses.append(available("metadata_api", "official_api", "YouTube metadata and search API is available."))
    else:
        statuses.append(
            needs_config(
                "metadata_api",
                "official_api",
                "YouTube metadata and search API is not configured.",
                "Set YOUTUBE_API_KEY in the process environment.",
            )
        )
    return statuses
