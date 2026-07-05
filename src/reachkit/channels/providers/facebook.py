from __future__ import annotations

import os

from reachkit.channels.models import ProviderStatus
from reachkit.channels.providers.common import available, needs_config


def provider_statuses() -> list[ProviderStatus]:
    if os.environ.get("FACEBOOK_ACCESS_TOKEN"):
        return [available("graph_api", "official_api", "Facebook Graph API access is configured.")]
    return [
        needs_config(
            "graph_api",
            "official_api",
            "Facebook Graph API access needs an explicit token.",
            "Set FACEBOOK_ACCESS_TOKEN for authorized Graph API reads.",
        )
    ]
