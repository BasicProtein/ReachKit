from __future__ import annotations

import argparse

from reachkit.core.formatting import to_json_text, to_plain_text
from reachkit.runtime.limits import DEFAULT_LIMIT, DEFAULT_MAX_CHARS, MAX_CHARS_LIMIT, MAX_LIMIT
from reachkit.sources.github import GitHubReader
from reachkit.sources.rss import RssReader
from reachkit.sources.web import WebReader


def _format_result(result, output_format: str) -> str:
    if output_format == "json":
        return to_json_text(result)
    return to_plain_text(result)


def _positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Value must be at least 1")
    return number


def bounded_limit(value: str) -> int:
    return min(_positive_int(value), MAX_LIMIT)


def bounded_max_chars(value: str) -> int:
    number = _positive_int(value)
    if number > MAX_CHARS_LIMIT:
        raise argparse.ArgumentTypeError(f"Value must be at most {MAX_CHARS_LIMIT}")
    return number


def handle_read_url(args: argparse.Namespace) -> int:
    result = WebReader().read(url=args.url, max_chars=args.max_chars)
    print(_format_result(result, args.format), end="")
    return 0


def handle_read_rss(args: argparse.Namespace) -> int:
    result = RssReader().read(url=args.url, limit=args.limit)
    print(_format_result(result, args.format), end="")
    return 0


def handle_read_github(args: argparse.Namespace) -> int:
    result = GitHubReader().read(repo=args.repo, path=args.path, ref=args.ref)
    print(_format_result(result, args.format), end="")
    return 0


def add_read_parser(subparsers) -> None:
    read_parser = subparsers.add_parser("read", help="Read public content.")
    read_subparsers = read_parser.add_subparsers(dest="read_source", required=True)

    url_parser = read_subparsers.add_parser("url", help="Read a public URL.")
    url_parser.add_argument("url")
    url_parser.add_argument("--format", choices=["text", "json"], default="text")
    url_parser.add_argument("--max-chars", type=bounded_max_chars, default=DEFAULT_MAX_CHARS)
    url_parser.set_defaults(handler=handle_read_url)

    rss_parser = read_subparsers.add_parser("rss", help="Read an RSS or Atom feed.")
    rss_parser.add_argument("url")
    rss_parser.add_argument("--limit", type=bounded_limit, default=DEFAULT_LIMIT)
    rss_parser.add_argument("--format", choices=["text", "json"], default="text")
    rss_parser.set_defaults(handler=handle_read_rss)

    github_parser = read_subparsers.add_parser("github", help="Read public GitHub content.")
    github_parser.add_argument("repo")
    github_parser.add_argument("--path")
    github_parser.add_argument("--ref")
    github_parser.add_argument("--format", choices=["text", "json"], default="text")
    github_parser.set_defaults(handler=handle_read_github)
