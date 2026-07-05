from __future__ import annotations

from collections.abc import Callable
import json
from typing import Any, TextIO

from reachkit.core.formatting import source_result_to_dict
from reachkit.core.models import SourceResult
from reachkit.sources.github import GitHubReader
from reachkit.sources.rss import RssReader
from reachkit.sources.web import WebReader

Handler = Callable[[dict[str, Any]], SourceResult]


def _tool_specs() -> list[dict[str, Any]]:
    return [
        {"name": "web_read", "arguments": {"url": "string", "max_chars": "integer optional"}},
        {"name": "rss_read", "arguments": {"url": "string", "limit": "integer optional"}},
        {"name": "github_read", "arguments": {"repo": "string", "path": "string optional", "ref": "string optional"}},
        {"name": "github_search", "arguments": {"query": "string", "limit": "integer optional"}},
    ]


class StdioServer:
    def __init__(
        self,
        web_read: Handler | None = None,
        rss_read: Handler | None = None,
        github_read: Handler | None = None,
        github_search: Handler | None = None,
    ) -> None:
        self._handlers: dict[str, Handler] = {
            "web_read": web_read or self._web_read,
            "rss_read": rss_read or self._rss_read,
            "github_read": github_read or self._github_read,
            "github_search": github_search or self._github_search,
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
        return {"id": request_id, "ok": True, "result": source_result_to_dict(result)}

    def _web_read(self, arguments: dict[str, Any]) -> SourceResult:
        url = _required_string(arguments, "url")
        max_chars = _optional_int(arguments, "max_chars")
        return WebReader().read(url=url, max_chars=max_chars)

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


def run_stdio_server(input_stream: TextIO, output_stream: TextIO) -> None:
    StdioServer().serve(input_stream, output_stream)
