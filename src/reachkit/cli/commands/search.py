from __future__ import annotations

import argparse

from reachkit.core.formatting import to_json_text, to_plain_text
from reachkit.runtime.limits import DEFAULT_LIMIT, MAX_LIMIT
from reachkit.sources.github import GitHubReader


def _positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Value must be at least 1")
    return number


def bounded_limit(value: str) -> int:
    return min(_positive_int(value), MAX_LIMIT)


def handle_search_github(args: argparse.Namespace) -> int:
    result = GitHubReader().search(args.query, limit=args.limit)
    if args.format == "json":
        print(to_json_text(result), end="")
    else:
        print(to_plain_text(result), end="")
    return 0


def add_search_parser(subparsers) -> None:
    search_parser = subparsers.add_parser("search", help="Search public indexes.")
    search_subparsers = search_parser.add_subparsers(dest="search_source", required=True)

    github_parser = search_subparsers.add_parser("github", help="Search public GitHub repositories.")
    github_parser.add_argument("query")
    github_parser.add_argument("--limit", type=bounded_limit, default=DEFAULT_LIMIT)
    github_parser.add_argument("--format", choices=["text", "json"], default="text")
    github_parser.set_defaults(handler=handle_search_github)
