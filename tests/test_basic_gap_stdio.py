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


def test_stdio_lists_basic_gap_tools():
    response = StdioServer().handle_line('{"id":"1","method":"tools/list","params":{}}')

    names = {tool["name"] for tool in response["result"]["tools"]}
    assert {"web_search", "youtube_metadata", "v2ex_read", "podcast_read", "xueqiu_hot"} <= names


def test_stdio_gap_tools_use_injected_handlers():
    server = StdioServer(
        web_search=lambda arguments: _result("web", arguments["query"]),
        v2ex_read=lambda arguments: _result("v2ex", arguments["target"]),
        podcast_read=lambda arguments: _result("podcast", arguments["url"]),
        xueqiu_hot=lambda arguments: _result("xueqiu", "Hot records"),
    )

    web = server.handle_line(
        '{"id":"2","method":"tools/call","params":{"name":"web_search","arguments":{"query":"agent","limit":1}}}'
    )
    v2ex = server.handle_line(
        '{"id":"3","method":"tools/call","params":{"name":"v2ex_read","arguments":{"target":"hot","limit":1}}}'
    )
    podcast = server.handle_line(
        '{"id":"4","method":"tools/call","params":{"name":"podcast_read","arguments":{"url":"https://example.com/feed.xml","limit":1}}}'
    )
    hot = server.handle_line(
        '{"id":"5","method":"tools/call","params":{"name":"xueqiu_hot","arguments":{"limit":2}}}'
    )

    assert web["result"]["title"] == "agent"
    assert v2ex["result"]["title"] == "hot"
    assert podcast["result"]["title"] == "https://example.com/feed.xml"
    assert hot["result"]["title"] == "Hot records"


def test_stdio_example_file_includes_basic_gap_tools():
    names = set()
    with open("examples/stdio-request.jsonl", encoding="utf-8") as handle:
        for line in handle:
            request = json.loads(line)
            params = request.get("params", {})
            if request.get("method") == "tools/call":
                names.add(params.get("name"))

    assert {"web_search", "youtube_metadata", "v2ex_read", "podcast_read", "xueqiu_hot"} <= names
