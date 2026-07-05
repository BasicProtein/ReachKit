from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import tomllib
from typing import Any

from reachkit.config.paths import config_path
from reachkit.core.errors import ConfigError

Settings = dict[str, Any]


def load_settings(path: str | Path | None = None) -> Settings:
    active_path = Path(path) if path is not None else config_path()
    if not active_path.exists():
        return {}
    try:
        return tomllib.loads(active_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError("ReachKit config could not be parsed") from exc
    except OSError as exc:
        raise ConfigError("ReachKit config could not be read") from exc


def save_settings(settings: Mapping[str, Any], path: str | Path | None = None) -> Path:
    active_path = Path(path) if path is not None else config_path()
    try:
        active_path.parent.mkdir(parents=True, exist_ok=True)
        active_path.write_text(_to_toml(settings), encoding="utf-8")
    except OSError as exc:
        raise ConfigError("ReachKit config could not be written") from exc
    return active_path


def set_auth_value(channel: str, key: str, value: str, path: str | Path | None = None) -> Path:
    settings = load_settings(path)
    auth = _ensure_table(settings, "auth")
    channel_table = _ensure_table(auth, channel)
    channel_table[key] = value
    return save_settings(settings, path)


def get_auth_value(channel: str, key: str, settings: Mapping[str, Any] | None = None) -> str | None:
    active_settings = settings if settings is not None else load_settings()
    value = active_settings.get("auth", {}).get(channel, {}).get(key)
    return value if isinstance(value, str) and value else None


def _ensure_table(table: Settings, key: str) -> Settings:
    value = table.get(key)
    if not isinstance(value, dict):
        value = {}
        table[key] = value
    return value


def _to_toml(settings: Mapping[str, Any]) -> str:
    lines: list[str] = []
    scalar_items = {key: value for key, value in settings.items() if not isinstance(value, Mapping)}
    for key in sorted(scalar_items):
        lines.append(f"{key} = {_format_value(scalar_items[key])}")
    for section in sorted(key for key, value in settings.items() if isinstance(value, Mapping)):
        if lines:
            lines.append("")
        _write_table(lines, [section], settings[section])
    return "\n".join(lines).rstrip() + "\n"


def _write_table(lines: list[str], path: list[str], table: Mapping[str, Any]) -> None:
    scalar_items = {key: value for key, value in table.items() if not isinstance(value, Mapping)}
    if scalar_items:
        lines.append(f"[{'.'.join(path)}]")
        for key in sorted(scalar_items):
            lines.append(f"{key} = {_format_value(scalar_items[key])}")
    for section in sorted(key for key, value in table.items() if isinstance(value, Mapping)):
        if lines and lines[-1] != "":
            lines.append("")
        _write_table(lines, [*path, section], table[section])


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if value is None:
        return '""'
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'
