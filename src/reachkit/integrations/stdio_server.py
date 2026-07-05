from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
import json
from typing import Any, TextIO

from reachkit.auth.checks import auth_status
from reachkit.channels.diagnostics import diagnose_channels
from reachkit.core.formatting import source_result_to_dict
from reachkit.core.models import SourceResult
from reachkit.sources.bilibili import BilibiliVideoReader
from reachkit.sources.browser import BrowserReader
from reachkit.sources.github import GitHubReader
from reachkit.sources.reddit import RedditReader
from reachkit.sources.rss import RssReader
from reachkit.sources.podcast import PodcastReader
from reachkit.sources.v2ex import V2EXReader
from reachkit.sources.xueqiu import XueqiuReader
from reachkit.sources.web import WebReader, WebSearchReader
from reachkit.sources.x_platform import XPostReader
from reachkit.sources.xiaohongshu import XiaohongshuApiReader
from reachkit.sources.youtube import YouTubeMetadataReader, YouTubeSearchReader, YouTubeTranscriptReader
from reachkit.setup.planner import build_setup_plan

Handler = Callable[[dict[str, Any]], SourceResult | dict[str, Any]]


def _tool_specs() -> list[dict[str, Any]]:
    return [
        {"name": "web_read", "arguments": {"url": "string", "max_chars": "integer optional", "cookie_file": "string optional", "storage_state": "string optional"}},
        {"name": "web_search", "arguments": {"query": "string", "limit": "integer optional"}},
        {"name": "rss_read", "arguments": {"url": "string", "limit": "integer optional"}},
        {"name": "github_read", "arguments": {"repo": "string", "path": "string optional", "ref": "string optional"}},
        {"name": "github_search", "arguments": {"query": "string", "limit": "integer optional"}},
        {"name": "youtube_transcript", "arguments": {"video": "string", "lang": "string optional", "max_chars": "integer optional"}},
        {"name": "youtube_metadata", "arguments": {"video": "string"}},
        {"name": "youtube_search", "arguments": {"query": "string", "limit": "integer optional"}},
        {"name": "x_read", "arguments": {"post": "string"}},
        {"name": "x_search", "arguments": {"query": "string", "limit": "integer optional"}},
        {"name": "bilibili_read", "arguments": {"video": "string"}},
        {"name": "bilibili_search", "arguments": {"query": "string", "limit": "integer optional"}},
        {"name": "xiaohongshu_api", "arguments": {"path": "string", "query": "object optional"}},
        {"name": "xiaohongshu_read", "arguments": {"path": "string", "query": "object optional"}},
        {"name": "reddit_read", "arguments": {"target": "string", "limit": "integer optional"}},
        {"name": "reddit_search", "arguments": {"query": "string", "limit": "integer optional"}},
        {"name": "v2ex_read", "arguments": {"target": "string", "limit": "integer optional"}},
        {"name": "podcast_read", "arguments": {"url": "string", "limit": "integer optional"}},
        {"name": "xueqiu_quote", "arguments": {"symbol": "string"}},
        {"name": "xueqiu_hot", "arguments": {"limit": "integer optional"}},
        {"name": "browser_read", "arguments": {"url": "string", "storage_state": "string optional", "wait_until": "string optional", "max_chars": "integer optional"}},
        {"name": "channels_list", "arguments": {}},
        {"name": "channels_doctor", "arguments": {"channel": "string optional"}},
        {"name": "auth_status", "arguments": {}},
        {"name": "setup_plan", "arguments": {}},
    ]


class StdioServer:
    def __init__(
        self,
        web_read: Handler | None = None,
        web_search: Handler | None = None,
        rss_read: Handler | None = None,
        github_read: Handler | None = None,
        github_search: Handler | None = None,
        youtube_transcript: Handler | None = None,
        youtube_metadata: Handler | None = None,
        youtube_search: Handler | None = None,
        x_read: Handler | None = None,
        x_search: Handler | None = None,
        bilibili_read: Handler | None = None,
        bilibili_search: Handler | None = None,
        xiaohongshu_api: Handler | None = None,
        xiaohongshu_read: Handler | None = None,
        reddit_read: Handler | None = None,
        reddit_search: Handler | None = None,
        v2ex_read: Handler | None = None,
        podcast_read: Handler | None = None,
        xueqiu_quote: Handler | None = None,
        xueqiu_hot: Handler | None = None,
        browser_read: Handler | None = None,
        channels_list: Handler | None = None,
        channels_doctor: Handler | None = None,
        auth_status_handler: Handler | None = None,
        setup_plan: Handler | None = None,
    ) -> None:
        self._handlers: dict[str, Handler] = {
            "web_read": web_read or self._web_read,
            "web_search": web_search or self._web_search,
            "rss_read": rss_read or self._rss_read,
            "github_read": github_read or self._github_read,
            "github_search": github_search or self._github_search,
            "youtube_transcript": youtube_transcript or self._youtube_transcript,
            "youtube_metadata": youtube_metadata or self._youtube_metadata,
            "youtube_search": youtube_search or self._youtube_search,
            "x_read": x_read or self._x_read,
            "x_search": x_search or self._x_search,
            "bilibili_read": bilibili_read or self._bilibili_read,
            "bilibili_search": bilibili_search or self._bilibili_search,
            "xiaohongshu_api": xiaohongshu_api or self._xiaohongshu_api,
            "xiaohongshu_read": xiaohongshu_read or self._xiaohongshu_api,
            "reddit_read": reddit_read or self._reddit_read,
            "reddit_search": reddit_search or self._reddit_search,
            "v2ex_read": v2ex_read or self._v2ex_read,
            "podcast_read": podcast_read or self._podcast_read,
            "xueqiu_quote": xueqiu_quote or self._xueqiu_quote,
            "xueqiu_hot": xueqiu_hot or self._xueqiu_hot,
            "browser_read": browser_read or self._browser_read,
            "channels_list": channels_list or self._channels_list,
            "channels_doctor": channels_doctor or self._channels_doctor,
            "auth_status": auth_status_handler or self._auth_status,
            "setup_plan": setup_plan or self._setup_plan,
        }

    def serve(self, input_stream: TextIO, output_stream: TextIO) -> None:
        for line in input_stream:
            if not line.strip():
                continue
            response = self.handle_line(line)
            output_stream.write(json.dumps(response, ensure_ascii=False, sort_keys=True) + "\n")
            output_stream.flush()

    def handle_line(self, line: str) -> dict[str, Any]:
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            return self._error(None, "invalid_json", "Invalid JSON")
        request_id = request.get("id") if isinstance(request, dict) else None
        if not isinstance(request, dict):
            return self._error(request_id, "invalid_request", "Invalid request")
        method = request.get("method")
        params = request.get("params", {})
        if not isinstance(params, dict):
            return self._error(request_id, "invalid_request", "Invalid request")
        if method == "tools/list":
            return {"id": request_id, "ok": True, "result": {"tools": _tool_specs()}}
        if method == "tools/call":
            return self._handle_tool_call(request_id, params)
        return self._error(request_id, "unknown_method", "Unknown method")

    def _handle_tool_call(self, request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(name, str) or not isinstance(arguments, dict):
            return self._error(request_id, "invalid_arguments", "Invalid tool arguments")
        handler = self._handlers.get(name)
        if handler is None:
            return self._error(request_id, "unknown_tool", "Unknown tool")
        try:
            result = handler(arguments)
        except Exception as exc:
            return self._error(request_id, "tool_error", str(exc) or "Tool call failed")
        payload = source_result_to_dict(result) if isinstance(result, SourceResult) else result
        return {"id": request_id, "ok": True, "result": payload}

    def _web_read(self, arguments: dict[str, Any]) -> SourceResult:
        url = _required_string(arguments, "url")
        max_chars = _optional_int(arguments, "max_chars")
        cookie_file = _optional_string(arguments, "cookie_file")
        storage_state = _optional_string(arguments, "storage_state")
        return WebReader().read(url=url, max_chars=max_chars, cookie_file=cookie_file, storage_state=storage_state)

    def _web_search(self, arguments: dict[str, Any]) -> SourceResult:
        query = _required_string(arguments, "query")
        limit = _optional_int(arguments, "limit") or 10
        return WebSearchReader().search(query=query, limit=limit)

    def _rss_read(self, arguments: dict[str, Any]) -> SourceResult:
        url = _required_string(arguments, "url")
        limit = _optional_int(arguments, "limit") or 10
        return RssReader().read(url=url, limit=limit)

    def _github_read(self, arguments: dict[str, Any]) -> SourceResult:
        repo = _required_string(arguments, "repo")
        path = _optional_string(arguments, "path")
        ref = _optional_string(arguments, "ref")
        return GitHubReader().read(repo=repo, path=path, ref=ref)

    def _github_search(self, arguments: dict[str, Any]) -> SourceResult:
        query = _required_string(arguments, "query")
        limit = _optional_int(arguments, "limit") or 10
        return GitHubReader().search(query=query, limit=limit)

    def _youtube_transcript(self, arguments: dict[str, Any]) -> SourceResult:
        video = _required_string(arguments, "video")
        lang = _optional_string(arguments, "lang") or "en"
        max_chars = _optional_int(arguments, "max_chars")
        return YouTubeTranscriptReader().read(video=video, lang=lang, max_chars=max_chars)

    def _youtube_metadata(self, arguments: dict[str, Any]) -> SourceResult:
        video = _required_string(arguments, "video")
        return YouTubeMetadataReader().read(video=video)

    def _youtube_search(self, arguments: dict[str, Any]) -> SourceResult:
        query = _required_string(arguments, "query")
        limit = _optional_int(arguments, "limit") or 10
        return YouTubeSearchReader().search(query=query, limit=limit)

    def _x_read(self, arguments: dict[str, Any]) -> SourceResult:
        post = _required_string(arguments, "post")
        return XPostReader().read(post)

    def _x_search(self, arguments: dict[str, Any]) -> SourceResult:
        query = _required_string(arguments, "query")
        limit = _optional_int(arguments, "limit") or 10
        return XPostReader().search(query=query, limit=limit)

    def _bilibili_read(self, arguments: dict[str, Any]) -> SourceResult:
        video = _required_string(arguments, "video")
        return BilibiliVideoReader().read(video)

    def _bilibili_search(self, arguments: dict[str, Any]) -> SourceResult:
        query = _required_string(arguments, "query")
        limit = _optional_int(arguments, "limit") or 10
        return BilibiliVideoReader().search(query=query, limit=limit)

    def _xiaohongshu_api(self, arguments: dict[str, Any]) -> SourceResult:
        path = _required_string(arguments, "path")
        query = _optional_string_dict(arguments, "query")
        return XiaohongshuApiReader().read(path=path, query=query)

    def _reddit_read(self, arguments: dict[str, Any]) -> SourceResult:
        target = _required_string(arguments, "target")
        limit = _optional_int(arguments, "limit") or 10
        return RedditReader().read(target=target, limit=limit)

    def _reddit_search(self, arguments: dict[str, Any]) -> SourceResult:
        query = _required_string(arguments, "query")
        limit = _optional_int(arguments, "limit") or 10
        return RedditReader().search(query=query, limit=limit)

    def _v2ex_read(self, arguments: dict[str, Any]) -> SourceResult:
        target = _required_string(arguments, "target")
        limit = _optional_int(arguments, "limit") or 10
        return V2EXReader().read(target=target, limit=limit)

    def _podcast_read(self, arguments: dict[str, Any]) -> SourceResult:
        url = _required_string(arguments, "url")
        limit = _optional_int(arguments, "limit") or 10
        return PodcastReader().read(url=url, limit=limit)

    def _xueqiu_quote(self, arguments: dict[str, Any]) -> SourceResult:
        symbol = _required_string(arguments, "symbol")
        return XueqiuReader().quote(symbol)

    def _xueqiu_hot(self, arguments: dict[str, Any]) -> SourceResult:
        limit = _optional_int(arguments, "limit") or 10
        return XueqiuReader().hot(limit=limit)

    def _browser_read(self, arguments: dict[str, Any]) -> SourceResult:
        url = _required_string(arguments, "url")
        storage_state = _optional_string(arguments, "storage_state")
        wait_until = _optional_string(arguments, "wait_until") or "load"
        max_chars = _optional_int(arguments, "max_chars")
        return BrowserReader().read(url=url, storage_state=storage_state, wait_until=wait_until, max_chars=max_chars)

    def _channels_list(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"channels": [asdict(status) for status in diagnose_channels()]}

    def _channels_doctor(self, arguments: dict[str, Any]) -> dict[str, Any]:
        channel = _optional_string(arguments, "channel")
        return {"channels": [asdict(status) for status in diagnose_channels(name=channel)]}

    def _auth_status(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"checks": [asdict(check) for check in auth_status()]}

    def _setup_plan(self, arguments: dict[str, Any]) -> dict[str, Any]:
        plan = build_setup_plan()
        return {"config_file": str(plan.config_file), "actions": [asdict(action) for action in plan.actions]}

    def _error(self, request_id: Any, code: str, message: str) -> dict[str, Any]:
        return {"id": request_id, "ok": False, "error": {"code": code, "message": message}}


def _required_string(arguments: dict[str, Any], name: str) -> str:
    value = arguments.get(name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Missing argument: {name}")
    return value


def _optional_string(arguments: dict[str, Any], name: str) -> str | None:
    value = arguments.get(name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Invalid argument: {name}")
    return value


def _optional_int(arguments: dict[str, Any], name: str) -> int | None:
    value = arguments.get(name)
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValueError(f"Invalid argument: {name}")
    return value


def _optional_string_dict(arguments: dict[str, Any], name: str) -> dict[str, str] | None:
    value = arguments.get(name)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError(f"Invalid argument: {name}")
    result: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise ValueError(f"Invalid argument: {name}")
        result[key] = item
    return result


def run_stdio_server(input_stream: TextIO, output_stream: TextIO) -> None:
    StdioServer().serve(input_stream, output_stream)
