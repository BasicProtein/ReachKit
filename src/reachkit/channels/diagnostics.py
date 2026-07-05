from __future__ import annotations

from reachkit.channels.models import ChannelDefinition, ChannelStatus, ProviderState, ProviderStatus
from reachkit.channels.registry import ChannelRegistry, default_channel_registry

_STATE_PRIORITY: dict[ProviderState, int] = {
    "available": 0,
    "needs_config": 1,
    "missing_dependency": 2,
    "failed": 3,
    "unsupported": 4,
}


def diagnose_channels(name: str | None = None, registry: ChannelRegistry | None = None) -> list[ChannelStatus]:
    active_registry = registry or default_channel_registry()
    channels = [active_registry.get(name)] if name else active_registry.all()
    return [_diagnose_definition(channel) for channel in channels]


def diagnose_channel(name: str, registry: ChannelRegistry | None = None) -> ChannelStatus:
    return diagnose_channels(name=name, registry=registry)[0]


def _diagnose_definition(channel: ChannelDefinition) -> ChannelStatus:
    providers: list[ProviderStatus] = []
    for check in channel.provider_checks:
        providers.extend(check())
    selected = _select_provider(providers)
    state = selected.state if selected else _best_state(providers)
    return ChannelStatus(
        name=channel.name,
        label=channel.label,
        capabilities=channel.capabilities,
        providers=providers,
        selected_provider=selected.name if selected else None,
        state=state,
    )


def _select_provider(providers: list[ProviderStatus]) -> ProviderStatus | None:
    available = [provider for provider in providers if provider.state == "available"]
    if not available:
        return None
    return sorted(available, key=lambda provider: _STATE_PRIORITY[provider.state])[0]


def _best_state(providers: list[ProviderStatus]) -> ProviderState:
    if not providers:
        return "unsupported"
    return sorted((provider.state for provider in providers), key=lambda state: _STATE_PRIORITY[state])[0]
