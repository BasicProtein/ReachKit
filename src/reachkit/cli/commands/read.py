from __future__ import annotations

import argparse

from reachkit.core.formatting import to_json_text, to_plain_text
from reachkit.runtime.limits import DEFAULT_LIMIT, DEFAULT_MAX_CHARS, MAX_CHARS_LIMIT, MAX_LIMIT
from reachkit.sources.bilibili import BilibiliVideoReader
from reachkit.sources.browser import BrowserReader
from reachkit.sources.github import GitHubReader
from reachkit.sources.rss import RssReader
from reachkit.sources.web import WebReader
from reachkit.sources.x_platform import XPostReader
from reachkit.sources.xiaohongshu import XiaohongshuApiReader
from reachkit.sources.youtube import YouTubeTranscriptReader


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
    result = WebReader().read(
        url=args.url,
        max_chars=args.max_chars,
        cookie_file=args.cookie_file,
        storage_state=args.storage_state,
    )
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


def handle_read_youtube(args: argparse.Namespace) -> int:
    result = YouTubeTranscriptReader().read(video=args.video, lang=args.lang, max_chars=args.max_chars)
    print(_format_result(result, args.format), end="")
    return 0


def handle_read_x(args: argparse.Namespace) -> int:
    result = XPostReader().read(args.post)
    print(_format_result(result, args.format), end="")
    return 0


def handle_read_bilibili(args: argparse.Namespace) -> int:
    result = BilibiliVideoReader().read(args.video)
    print(_format_result(result, args.format), end="")
    return 0


def handle_read_xiaohongshu(args: argparse.Namespace) -> int:
    result = XiaohongshuApiReader().read(path=args.path, query=_query_params(args.param))
    print(_format_result(result, args.format), end="")
    return 0


def handle_read_browser(args: argparse.Namespace) -> int:
    result = BrowserReader().read(
        url=args.url,
        storage_state=args.storage_state,
        wait_until=args.wait_until,
        max_chars=args.max_chars,
    )
    print(_format_result(result, args.format), end="")
    return 0


def _query_params(values: list[str] | None) -> dict[str, str]:
    params: dict[str, str] = {}
    for key, item_value in values or []:
        params[key] = item_value
    return params


def _query_param(value: str) -> tuple[str, str]:
    key, separator, item_value = value.partition("=")
    if not separator or not key:
        raise argparse.ArgumentTypeError("Query parameters must use key=value format")
    return key, item_value


def add_read_parser(subparsers) -> None:
    read_parser = subparsers.add_parser("read", help="Read public content.")
    read_subparsers = read_parser.add_subparsers(dest="read_source", required=True)

    url_parser = read_subparsers.add_parser("url", help="Read a public URL.")
    url_parser.add_argument("url")
    url_parser.add_argument("--format", choices=["text", "json"], default="text")
    url_parser.add_argument("--max-chars", type=bounded_max_chars, default=DEFAULT_MAX_CHARS)
    url_parser.add_argument("--cookie-file")
    url_parser.add_argument("--storage-state")
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

    youtube_parser = read_subparsers.add_parser("youtube", help="Read a public YouTube transcript.")
    youtube_parser.add_argument("video")
    youtube_parser.add_argument("--lang", default="en")
    youtube_parser.add_argument("--max-chars", type=bounded_max_chars, default=DEFAULT_MAX_CHARS)
    youtube_parser.add_argument("--format", choices=["text", "json"], default="text")
    youtube_parser.set_defaults(handler=handle_read_youtube)

    x_parser = read_subparsers.add_parser("x", help="Read a public X post through the official API.")
    x_parser.add_argument("post")
    x_parser.add_argument("--format", choices=["text", "json"], default="text")
    x_parser.set_defaults(handler=handle_read_x)

    bilibili_parser = read_subparsers.add_parser("bilibili", help="Read public Bilibili video metadata.")
    bilibili_parser.add_argument("video")
    bilibili_parser.add_argument("--format", choices=["text", "json"], default="text")
    bilibili_parser.set_defaults(handler=handle_read_bilibili)

    xhs_parser = read_subparsers.add_parser("xiaohongshu", help="Read Xiaohongshu open API JSON.")
    xhs_parser.add_argument("path")
    xhs_parser.add_argument("--param", action="append", type=_query_param)
    xhs_parser.add_argument("--format", choices=["text", "json"], default="text")
    xhs_parser.set_defaults(handler=handle_read_xiaohongshu)

    browser_parser = read_subparsers.add_parser("browser", help="Read rendered page text with an optional browser extra.")
    browser_parser.add_argument("url")
    browser_parser.add_argument("--storage-state")
    browser_parser.add_argument("--wait-until", choices=["commit", "domcontentloaded", "load", "networkidle"], default="load")
    browser_parser.add_argument("--max-chars", type=bounded_max_chars, default=DEFAULT_MAX_CHARS)
    browser_parser.add_argument("--format", choices=["text", "json"], default="text")
    browser_parser.set_defaults(handler=handle_read_browser)
