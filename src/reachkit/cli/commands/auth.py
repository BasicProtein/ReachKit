from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from reachkit.auth.checks import auth_status, validate_cookie_file, validate_storage_state
from reachkit.config.settings import set_auth_value
from reachkit.core.errors import InputError


def _checks_to_json(checks) -> str:
    return json.dumps({"checks": [asdict(check) for check in checks]}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _checks_to_text(checks) -> str:
    lines: list[str] = []
    for check in checks:
        lines.append(f"[{check.state}] {check.name}: {check.message}")
        if check.fix:
            lines.append(f"  fix: {check.fix}")
    return "\n".join(lines).rstrip() + "\n"


def handle_auth_status(args: argparse.Namespace) -> int:
    checks = auth_status()
    if args.format == "json":
        print(_checks_to_json(checks), end="")
    else:
        print(_checks_to_text(checks), end="")
    return 0


def handle_auth_set(args: argparse.Namespace) -> int:
    if args.auth_target in {"github", "x"}:
        if not args.token_env:
            raise InputError("--token-env is required for this target")
        set_auth_value(args.auth_target, "token_env", args.token_env)
        print(f"Configured {args.auth_target} token env: {args.token_env}")
        return 0
    if args.auth_target == "xiaohongshu":
        if not args.app_key_env or not args.app_secret_env:
            raise InputError("--app-key-env and --app-secret-env are required for this target")
        set_auth_value("xiaohongshu", "app_key_env", args.app_key_env)
        set_auth_value("xiaohongshu", "app_secret_env", args.app_secret_env)
        print("Configured xiaohongshu app credential env names")
        return 0
    if args.auth_target == "browser":
        if not args.storage_state:
            raise InputError("--storage-state is required for browser")
        try:
            validate_storage_state(args.storage_state)
        except Exception as exc:
            raise InputError("storage-state file could not be read") from exc
        set_auth_value("browser", "storage_state", args.storage_state)
        print(f"Configured browser storage-state: {args.storage_state}")
        return 0
    if args.auth_target == "web":
        if not args.cookie_file:
            raise InputError("--cookie-file is required for web")
        try:
            validate_cookie_file(args.cookie_file)
        except Exception as exc:
            raise InputError("cookie file could not be read") from exc
        set_auth_value("web", "cookie_file", args.cookie_file)
        print(f"Configured web cookie file: {args.cookie_file}")
        return 0
    raise InputError("Unknown auth target")


def add_auth_parser(subparsers) -> None:
    parser = subparsers.add_parser("auth", help="Inspect and configure explicit credentials.")
    auth_subparsers = parser.add_subparsers(dest="auth_command", required=True)

    status_parser = auth_subparsers.add_parser("status", help="Show configured credential inputs.")
    status_parser.add_argument("--format", choices=["text", "json"], default="text")
    status_parser.set_defaults(handler=handle_auth_status)

    set_parser = auth_subparsers.add_parser("set", help="Store credential environment names or explicit file paths.")
    set_parser.add_argument("auth_target", choices=["github", "x", "xiaohongshu", "browser", "web"])
    set_parser.add_argument("--token-env")
    set_parser.add_argument("--app-key-env")
    set_parser.add_argument("--app-secret-env")
    set_parser.add_argument("--storage-state")
    set_parser.add_argument("--cookie-file")
    set_parser.set_defaults(handler=handle_auth_set)
