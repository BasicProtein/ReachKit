from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

CapabilityKind = Literal["read", "search", "metadata", "comments", "timeline", "actions", "transcript"]
ProviderState = Literal["available", "needs_config", "missing_dependency", "unsupported", "failed"]
AccessKind = Literal["public", "official_api", "explicit_cookie", "explicit_browser_state", "manual_file"]


@dataclass(frozen=True)
class ChannelCapability:
    kind: CapabilityKind
    label: str
    requires_auth: bool = False


@dataclass(frozen=True)
class ProviderStatus:
    name: str
    state: ProviderState
    access: AccessKind
    message: str
    fix: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


ProviderCheck = Callable[[], list[ProviderStatus]]


@dataclass(frozen=True)
class ChannelStatus:
    name: str
    label: str
    capabilities: list[ChannelCapability]
    providers: list[ProviderStatus]
    selected_provider: str | None
    state: ProviderState


@dataclass(frozen=True)
class ChannelDefinition:
    name: str
    label: str
    capabilities: list[ChannelCapability]
    provider_checks: list[ProviderCheck]