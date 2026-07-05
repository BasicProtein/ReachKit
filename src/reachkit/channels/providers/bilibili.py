from __future__ import annotations

from reachkit.channels.models import ProviderStatus
from reachkit.channels.providers.common import available


def provider_statuses() -> list[ProviderStatus]:
    return [available("public_metadata", "public", "Public Bilibili video metadata access is available.")]
