from __future__ import annotations

import argparse

from reachkit.core.formatting import to_json_text, to_plain_text
from reachkit.runtime.limits import DEFAULT_LIMIT, MAX_LIMIT
from reachkit.sources.bilibili import BilibiliVideoReader
from reachkit.sources.github import GitHubReader
from reachkit.sources.reddit import RedditReader
from reachkit.sources.web import WebSearchReader
from reachkit.sources.x_platform import XPostReader
from reachkit.sources.xueqiu import XueqiuReader
from reachkit.sources.youtube import YouTubeSearchReader


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


def _print_result(result, output_format: str) -> int:
    if output_format == "json":
        print(to_json_text(result), end="")
    else:
        print(to_plain_text(result), end="")
    return 0


def handle_search_youtube(args: argparse.Namespace) -> int:
    return _print_result(YouTubeSearchReader().search(args.query, limit=args.limit), args.format)


def handle_search_bilibili(args: argparse.Namespace) -> int:
    return _print_result(BilibiliVideoReader().search(args.query, limit=args.limit), args.format)


def handle_search_x(args: argparse.Namespace) -> int:
    return _print_result(XPostReader().search(args.query, limit=args.limit), args.format)


def handle_search_reddit(args: argparse.Namespace) -> int:
    return _print_result(RedditReader().search(args.query, limit=args.limit), args.format)


def handle_search_xueqiu(args: argparse.Namespace) -> int:
    return _print_result(XueqiuReader().search(args.query, limit=args.limit), args.format)


def handle_search_web(args: argparse.Namespace) -> int:
    return _print_result(WebSearchReader().search(args.query, limit=args.limit), args.format)


def add_search_parser(subparsers) -> None:
    search_parser = subparsers.add_parser("search", help="Search public indexes.")
    search_subparsers = search_parser.add_subparsers(dest="search_source", required=True)

    web_parser = search_subparsers.add_parser("web", help="Search a configured web search endpoint.")
    web_parser.add_argument("query")
    web_parser.add_argument("--limit", type=bounded_limit, default=DEFAULT_LIMIT)
    web_parser.add_argument("--format", choices=["text", "json"], default="text")
    web_parser.set_defaults(handler=handle_search_web)

    github_parser = search_subparsers.add_parser("github", help="Search public GitHub repositories.")
    github_parser.add_argument("query")
    github_parser.add_argument("--limit", type=bounded_limit, default=DEFAULT_LIMIT)
    github_parser.add_argument("--format", choices=["text", "json"], default="text")
    github_parser.set_defaults(handler=handle_search_github)

    youtube_parser = search_subparsers.add_parser("youtube", help="Search YouTube videos with an explicit API key.")
    youtube_parser.add_argument("query")
    youtube_parser.add_argument("--limit", type=bounded_limit, default=DEFAULT_LIMIT)
    youtube_parser.add_argument("--format", choices=["text", "json"], default="text")
    youtube_parser.set_defaults(handler=handle_search_youtube)

    bilibili_parser = search_subparsers.add_parser("bilibili", help="Search public Bilibili videos.")
    bilibili_parser.add_argument("query")
    bilibili_parser.add_argument("--limit", type=bounded_limit, default=DEFAULT_LIMIT)
    bilibili_parser.add_argument("--format", choices=["text", "json"], default="text")
    bilibili_parser.set_defaults(handler=handle_search_bilibili)

    x_parser = search_subparsers.add_parser("x", help="Search X posts through the official API.")
    x_parser.add_argument("query")
    x_parser.add_argument("--limit", type=bounded_limit, default=DEFAULT_LIMIT)
    x_parser.add_argument("--format", choices=["text", "json"], default="text")
    x_parser.set_defaults(handler=handle_search_x)

    reddit_parser = search_subparsers.add_parser("reddit", help="Search public Reddit posts.")
    reddit_parser.add_argument("query")
    reddit_parser.add_argument("--limit", type=bounded_limit, default=DEFAULT_LIMIT)
    reddit_parser.add_argument("--format", choices=["text", "json"], default="text")
    reddit_parser.set_defaults(handler=handle_search_reddit)

    xueqiu_parser = search_subparsers.add_parser("xueqiu", help="Search Xueqiu stocks.")
    xueqiu_parser.add_argument("query")
    xueqiu_parser.add_argument("--limit", type=bounded_limit, default=DEFAULT_LIMIT)
    xueqiu_parser.add_argument("--format", choices=["text", "json"], default="text")
    xueqiu_parser.set_defaults(handler=handle_search_xueqiu)
