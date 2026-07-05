from __future__ import annotations

from reachkit.channels.models import ProviderStatus


def available(name: str, access: str, message: str) -> ProviderStatus:
    return ProviderStatus(name=name, state="available", access=access, message=message)


def needs_config(name: str, access: str, message: str, fix: str) -> ProviderStatus:
    return ProviderStatus(name=name, state="needs_config", access=access, message=message, fix=fix)


def missing_dependency(name: str, access: str, message: str, fix: str) -> ProviderStatus:
    return ProviderStatus(name=name, state="missing_dependency", access=access, message=message, fix=fix)
