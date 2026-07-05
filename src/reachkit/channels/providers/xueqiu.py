from __future__ import annotations

from reachkit.channels.models import ProviderStatus
from reachkit.channels.providers.common import available, needs_config


def provider_statuses() -> list[ProviderStatus]:
    return [
        available("public_quote", "public", "Public Xueqiu quote and search endpoints are available when reachable."),
        needs_config(
            "explicit_cookie",
            "explicit_cookie",
            "Some Xueqiu pages may require a user-provided cookie file.",
            "Configure a cookie file with reachkit auth set web when needed.",
        ),
    ]
