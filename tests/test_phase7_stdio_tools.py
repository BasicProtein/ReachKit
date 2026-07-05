from __future__ import annotations

import json

from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.integrations.stdio_server import StdioServer


def _result(source: str, title: str) -> SourceResult:
    return SourceResult(
        source=source,
        url=f"https://example.com/{source}",
        title=title,
        content_type="application/json",
        items=[RetrievedItem(title=title, url=None, text=f"{title} text", metadata={})],
    )


def test_tools_list_includes_agent_management_tools():
    response = StdioServer().handle_line('{"id":"1","method":"tools/list","params":{}}')

    names = [tool["name"] for tool in response["result"]["tools"]]
    assert {"channels_list", "channels_doctor", "auth_status", "setup_plan"} <= set(names)
    assert {"youtube_search", "bilibili_search", "reddit_read", "x_search", "xiaohongshu_read"} <= set(names)


def test_channels_list_tool_returns_plain_status_payload():
    response = StdioServer().handle_line(
        '{"id":"2","method":"tools/call","params":{"name":"channels_list","arguments":{}}}'
    )

    assert response["ok"] is True
    assert "channels" in response["result"]
    assert any(channel["name"] == "github" for channel in response["result"]["channels"])


def test_auth_status_and_setup_plan_tools_return_json_safe_payloads(tmp_path, monkeypatch):
    monkeypatch.setenv("REACHKIT_CONFIG", str(tmp_path / "config.toml"))

    auth_response = StdioServer().handle_line(
        '{"id":"3","method":"tools/call","params":{"name":"auth_status","arguments":{}}}'
    )
    setup_response = StdioServer().handle_line(
        '{"id":"4","method":"tools/call","params":{"name":"setup_plan","arguments":{}}}'
    )

    assert auth_response["ok"] is True
    assert "checks" in auth_response["result"]
    assert setup_response["ok"] is True
    assert "actions" in setup_response["result"]


def test_new_stdio_read_and_search_tools_use_injected_handlers():
    server = StdioServer(
        youtube_search=lambda arguments: _result("youtube", arguments["query"]),
        reddit_read=lambda arguments: _result("reddit", arguments["target"]),
        x_search=lambda arguments: _result("x", arguments["query"]),
    )

    youtube = server.handle_line(
        '{"id":"5","method":"tools/call","params":{"name":"youtube_search","arguments":{"query":"agent","limit":1}}}'
    )
    reddit = server.handle_line(
        '{"id":"6","method":"tools/call","params":{"name":"reddit_read","arguments":{"target":"abc","limit":1}}}'
    )
    x_search = server.handle_line(
        '{"id":"7","method":"tools/call","params":{"name":"x_search","arguments":{"query":"agent","limit":1}}}'
    )

    assert youtube["result"]["title"] == "agent"
    assert reddit["result"]["title"] == "abc"
    assert x_search["result"]["title"] == "agent"
