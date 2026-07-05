from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from reachkit import __version__
from reachkit.cli.commands.doctor import add_doctor_parser
from reachkit.cli.commands.read import add_read_parser
from reachkit.cli.commands.search import add_search_parser
from reachkit.cli.commands.serve import add_serve_parser
from reachkit.core.errors import ReachKitError


def _prefer_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reachkit",
        description="ReachKit reads public web, RSS, and GitHub content.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the package version and exit.",
    )
    subparsers = parser.add_subparsers(dest="command")
    add_read_parser(subparsers)
    add_search_parser(subparsers)
    add_doctor_parser(subparsers)
    add_serve_parser(subparsers)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _prefer_utf8_stdio()
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if args.version:
            print(__version__)
            return 0
        handler = getattr(args, "handler", None)
        if handler is None:
            parser.print_help(sys.stdout)
            return 0
        return int(handler(args))
    except SystemExit as exc:
        return int(exc.code)
    except ReachKitError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 3
