from __future__ import annotations

import argparse

from reachkit.core.formatting import diagnostic_issues_to_json_text, diagnostic_issues_to_plain_text
from reachkit.diagnostics.doctor import required_checks_failed, run_doctor


def handle_doctor(args: argparse.Namespace) -> int:
    issues = run_doctor()
    if args.format == "json":
        print(diagnostic_issues_to_json_text(issues), end="")
    else:
        print(diagnostic_issues_to_plain_text(issues), end="")
    return 1 if required_checks_failed(issues) else 0


def add_doctor_parser(subparsers) -> None:
    parser = subparsers.add_parser("doctor", help="Check local readiness.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.set_defaults(handler=handle_doctor)
