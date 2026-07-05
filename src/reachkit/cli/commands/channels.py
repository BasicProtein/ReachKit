from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from reachkit.channels.diagnostics import diagnose_channels
from reachkit.channels.registry import default_channel_registry


def _capability_names(capabilities) -> str:
    return ", ".join(capability.kind for capability in capabilities)


def _channels_to_json(statuses) -> str:
    payload = {"channels": [asdict(status) for status in statuses]}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _channels_to_plain_text(statuses) -> str:
    lines: list[str] = []
    for status in statuses:
        lines.append(f"[{status.state}] {status.name}: {_capability_names(status.capabilities)}")
        if status.selected_provider:
            lines.append(f"  selected: {status.selected_provider}")
        for provider in status.providers:
            detail = f"  - {provider.name}: {provider.state} ({provider.access}) - {provider.message}"
            lines.append(detail)
            if provider.fix:
                lines.append(f"    fix: {provider.fix}")
    return "\n".join(lines).rstrip() + "\n"


def handle_channels_list(args: argparse.Namespace) -> int:
    statuses = diagnose_channels(registry=default_channel_registry())
    if args.format == "json":
        print(_channels_to_json(statuses), end="")
    else:
        print(_channels_to_plain_text(statuses), end="")
    return 0


def handle_channels_doctor(args: argparse.Namespace) -> int:
    statuses = diagnose_channels(name=args.channel)
    if args.format == "json":
        print(_channels_to_json(statuses), end="")
    else:
        print(_channels_to_plain_text(statuses), end="")
    return 0


def add_channels_parser(subparsers) -> None:
    parser = subparsers.add_parser("channels", help="Inspect platform capabilities.")
    channel_subparsers = parser.add_subparsers(dest="channels_command", required=True)

    list_parser = channel_subparsers.add_parser("list", help="List configured platform capabilities.")
    list_parser.add_argument("--format", choices=["text", "json"], default="text")
    list_parser.set_defaults(handler=handle_channels_list)

    doctor_parser = channel_subparsers.add_parser("doctor", help="Check platform provider readiness.")
    doctor_parser.add_argument("channel", nargs="?")
    doctor_parser.add_argument("--format", choices=["text", "json"], default="text")
    doctor_parser.set_defaults(handler=handle_channels_doctor)
