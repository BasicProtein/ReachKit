from __future__ import annotations

from reachkit.channels.models import ProviderStatus
from reachkit.channels.providers.common import available, needs_config


def provider_statuses() -> list[ProviderStatus]:
    return [
        available("public_page", "public", "Public LinkedIn page reads are available."),
        needs_config(
            "authorized_state",
            "explicit_browser_state",
            "Authorized LinkedIn flows require an explicit browser state file.",
            "Configure a storage-state file only for pages you are allowed to access.",
        ),
    ]
