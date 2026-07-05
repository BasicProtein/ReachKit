from __future__ import annotations

import json
import os
from pathlib import Path

from reachkit.auth.models import AuthCheck
from reachkit.config.settings import get_auth_value, load_settings
from reachkit.runtime.cookies import load_cookie_header


def auth_status() -> list[AuthCheck]:
    settings = load_settings()
    return [
        _env_token_check("github", "token_env", "GITHUB_TOKEN", "github_token", settings),
        _env_token_check("x", "token_env", "X_BEARER_TOKEN", "x_token", settings),
        _env_token_check("xiaohongshu", "app_key_env", "XHS_APP_KEY", "xiaohongshu_app_key", settings),
        _env_token_check("xiaohongshu", "app_secret_env", "XHS_APP_SECRET", "xiaohongshu_app_secret", settings),
        _env_token_check("facebook", "token_env", "FACEBOOK_ACCESS_TOKEN", "facebook_token", settings),
        _env_token_check("instagram", "token_env", "INSTAGRAM_ACCESS_TOKEN", "instagram_token", settings),
        _path_check("browser", "storage_state", "browser_storage_state", "storage-state", _validate_storage_state, settings),
        _path_check("web", "cookie_file", "web_cookie_file", "cookie file", _validate_cookie_file, settings),
    ]


def validate_storage_state(path: str) -> None:
    _validate_storage_state(Path(path))


def validate_cookie_file(path: str) -> None:
    _validate_cookie_file(Path(path))


def _env_token_check(channel: str, key: str, default_env: str, name: str, settings) -> AuthCheck:
    env_name = get_auth_value(channel, key, settings) or default_env
    if os.environ.get(env_name):
        return AuthCheck(name=name, state="configured", message=f"Environment variable {env_name} is set")
    return AuthCheck(
        name=name,
        state="missing",
        message=f"Environment variable {env_name} is not set",
        fix=f"Set {env_name} or configure a different env name with reachkit auth set",
    )


def _path_check(channel: str, key: str, name: str, label: str, validator, settings) -> AuthCheck:
    value = get_auth_value(channel, key, settings)
    if not value:
        return AuthCheck(
            name=name,
            state="missing",
            message=f"No {label} is configured",
            fix=f"Configure one with reachkit auth set",
        )
    path = Path(value)
    try:
        validator(path)
    except Exception:
        return AuthCheck(
            name=name,
            state="invalid",
            message=f"Configured {label} cannot be used: {path}",
            fix=f"Check the file path and readability",
        )
    return AuthCheck(name=name, state="configured", message=f"Configured {label}: {path}")


def _validate_storage_state(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("storage-state must be an object")
    if "cookies" in data and not isinstance(data["cookies"], list):
        raise ValueError("storage-state cookies must be a list")


def _validate_cookie_file(path: Path) -> None:
    load_cookie_header(path)
