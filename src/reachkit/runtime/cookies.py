from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reachkit.core.errors import InputError, ParseError


def load_cookie_header(path: str | Path) -> str:
    cookie_path = Path(path)
    try:
        text = cookie_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError("Cookie file could not be read") from exc

    stripped = text.lstrip()
    if stripped.startswith("[") or stripped.startswith("{"):
        pairs = _load_json_pairs(stripped)
    else:
        pairs = _load_netscape_pairs(text)
    if not pairs:
        raise ParseError("Cookie file did not contain usable cookies")
    return "; ".join(f"{name}={value}" for name, value in pairs)


def _load_json_pairs(text: str) -> list[tuple[str, str]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ParseError("Cookie JSON was not valid") from exc
    records: list[Any]
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and isinstance(data.get("cookies"), list):
        records = data["cookies"]
    else:
        raise ParseError("Cookie JSON must be a list or an object with cookies")
    pairs: list[tuple[str, str]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        name = record.get("name")
        value = record.get("value")
        if isinstance(name, str) and name and isinstance(value, str):
            pairs.append((name, value))
    return pairs


def _load_netscape_pairs(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 7:
            continue
        name = parts[5].strip()
        value = parts[6].strip()
        if name:
            pairs.append((name, value))
    return pairs
