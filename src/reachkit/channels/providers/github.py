from __future__ import annotations

import os

from reachkit.channels.models import ProviderStatus
from reachkit.channels.providers.common import available


def provider_statuses() -> list[ProviderStatus]:
    statuses = [available("public_api", "public", "Public GitHub API access is available.")]
    if os.environ.get("GITHUB_TOKEN"):
        statuses.append(available("token_api", "official_api", "GitHub token API access is configured."))
    return statuses
