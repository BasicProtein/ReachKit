from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from reachkit.setup.executor import SetupExecutionResult, execute_install_plan
from reachkit.setup.planner import SetupPlan, build_setup_plan
from reachkit.setup.uninstall import RemoveResult, remove_reachkit_state


def _plan_to_json(plan: SetupPlan) -> str:
    payload = {
        "config_file": str(plan.config_file),
        "actions": [asdict(action) for action in plan.actions],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _plan_to_text(plan: SetupPlan) -> str:
    lines = [f"Config file: {plan.config_file}", "Actions:"]
    for action in plan.actions:
        marker = "required" if action.required else "optional"
        lines.append(f"- {action.name} [{action.kind}, {marker}]: {action.description}")
        if action.command:
            lines.append(f"  command: {' '.join(action.command)}")
    return "\n".join(lines).rstrip() + "\n"


def _execution_to_text(result: SetupExecutionResult) -> str:
    lines: list[str] = []
    for item in result.items:
        state = "executed" if item.executed else item.message
        lines.append(f"- {item.action.name}: {state}")
    return "\n".join(lines).rstrip() + "\n"


def _execution_to_json(result: SetupExecutionResult) -> str:
    payload = {
        "actions": [
            {"action": asdict(item.action), "executed": item.executed, "message": item.message}
            for item in result.items
        ]
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _remove_to_text(result: RemoveResult) -> str:
    if result.purged:
        if result.removed:
            return f"Removed ReachKit config: {result.config_file}\n"
        return f"ReachKit config was already absent: {result.config_file}\n"
    if result.kept:
        return f"ReachKit config kept: {result.config_file}\n"
    return f"No ReachKit config found: {result.config_file}\n"


def _remove_to_json(result: RemoveResult) -> str:
    payload = {
        "purged": result.purged,
        "config_file": str(result.config_file),
        "removed": [str(path) for path in result.removed],
        "kept": [str(path) for path in result.kept],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def handle_setup_plan(args: argparse.Namespace) -> int:
    plan = build_setup_plan()
    if args.format == "json":
        print(_plan_to_json(plan), end="")
    else:
        print(_plan_to_text(plan), end="")
    return 0


def handle_setup_install(args: argparse.Namespace) -> int:
    plan = build_setup_plan()
    result = execute_install_plan(plan, dry_run=args.dry_run, safe=args.safe)
    if args.format == "json":
        print(_execution_to_json(result), end="")
    else:
        print(_execution_to_text(result), end="")
    return 0


def handle_setup_update(args: argparse.Namespace) -> int:
    plan = build_setup_plan()
    result = execute_install_plan(plan, dry_run=args.dry_run, safe=args.safe)
    if args.format == "json":
        print(_execution_to_json(result), end="")
    else:
        print(_execution_to_text(result), end="")
    return 0


def handle_setup_remove(args: argparse.Namespace) -> int:
    result = remove_reachkit_state(purge=args.purge)
    if args.format == "json":
        print(_remove_to_json(result), end="")
    else:
        print(_remove_to_text(result), end="")
    return 0


def add_setup_parser(subparsers) -> None:
    parser = subparsers.add_parser("setup", help="Plan and manage local ReachKit setup.")
    setup_subparsers = parser.add_subparsers(dest="setup_command", required=True)

    plan_parser = setup_subparsers.add_parser("plan", help="Show the local setup plan.")
    plan_parser.add_argument("--format", choices=["text", "json"], default="text")
    plan_parser.set_defaults(handler=handle_setup_plan)

    install_parser = setup_subparsers.add_parser("install", help="Create local ReachKit setup files.")
    install_parser.add_argument("--dry-run", action="store_true")
    install_parser.add_argument("--safe", action="store_true")
    install_parser.add_argument("--format", choices=["text", "json"], default="text")
    install_parser.set_defaults(handler=handle_setup_install)

    update_parser = setup_subparsers.add_parser("update", help="Refresh local ReachKit setup files.")
    update_parser.add_argument("--dry-run", action="store_true")
    update_parser.add_argument("--safe", action="store_true")
    update_parser.add_argument("--format", choices=["text", "json"], default="text")
    update_parser.set_defaults(handler=handle_setup_update)

    remove_parser = setup_subparsers.add_parser("remove", help="Remove ReachKit setup state.")
    remove_parser.add_argument("--purge", action="store_true")
    remove_parser.add_argument("--format", choices=["text", "json"], default="text")
    remove_parser.set_defaults(handler=handle_setup_remove)
