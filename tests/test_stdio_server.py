from io import StringIO
import json

from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.integrations.stdio_server import StdioServer


def _result(url="https://example.com"):
    return SourceResult(
        source="web",
        url=url,
        title="Example",
        content_type="text/html",
        items=[RetrievedItem(title="Example", url=url, text="Hello")],
    )


def test_tools_list_response_contains_expected_tools():
    response = StdioServer().handle_line('{"id":"1","method":"tools/list","params":{}}')

    assert response["ok"] is True
    names = [tool["name"] for tool in response["result"]["tools"]]
    expected = [
        "web_read",
        "rss_read",
        "github_read",
        "github_search",
        "youtube_transcript",
        "x_read",
        "bilibili_read",
        "xiaohongshu_api",
        "browser_read",
    ]
    assert all(name in names for name in expected)
    assert [name for name in names if name in expected] == expected


def test_tools_call_uses_injected_handler():
    server = StdioServer(web_read=lambda arguments: _result(arguments["url"]))

    response = server.handle_line(
        '{"id":"2","method":"tools/call","params":{"name":"web_read","arguments":{"url":"https://example.com"}}}'
    )

    assert response["ok"] is True
    assert response["result"]["items"][0]["text"] == "Hello"


def test_tools_call_passes_cookie_file_to_web_handler():
    seen = []
    server = StdioServer(web_read=lambda arguments: seen.append(arguments) or _result(arguments["url"]))

    response = server.handle_line(
        '{"id":"2","method":"tools/call","params":{"name":"web_read","arguments":{"url":"https://example.com","cookie_file":"cookies.json","storage_state":"storage-state.json"}}}'
    )

    assert response["ok"] is True
    assert seen[0]["cookie_file"] == "cookies.json"
    assert seen[0]["storage_state"] == "storage-state.json"


def test_tools_call_passes_query_to_xiaohongshu_handler():
    seen = []
    server = StdioServer(xiaohongshu_api=lambda arguments: seen.append(arguments) or _result("https://example.com"))

    response = server.handle_line(
        '{"id":"2","method":"tools/call","params":{"name":"xiaohongshu_api","arguments":{"path":"/api/open/test","query":{"note_id":"abc"}}}}'
    )

    assert response["ok"] is True
    assert seen[0]["query"] == {"note_id": "abc"}


def test_invalid_json_returns_error():
    response = StdioServer().handle_line("{not-json")

    assert response["ok"] is False
    assert response["error"]["code"] == "invalid_json"


def test_unknown_tool_returns_error():
    response = StdioServer().handle_line(
        '{"id":"3","method":"tools/call","params":{"name":"missing","arguments":{}}}'
    )

    assert response["ok"] is False
    assert response["error"]["code"] == "unknown_tool"


def test_serve_reads_and_writes_json_lines():
    input_stream = StringIO('{"id":"1","method":"tools/list","params":{}}\n')
    output_stream = StringIO()

    StdioServer().serve(input_stream, output_stream)

    lines = output_stream.getvalue().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["ok"] is True
