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
    assert [tool["name"] for tool in response["result"]["tools"]] == [
        "web_read",
        "rss_read",
        "github_read",
        "github_search",
    ]


def test_tools_call_uses_injected_handler():
    server = StdioServer(web_read=lambda arguments: _result(arguments["url"]))

    response = server.handle_line(
        '{"id":"2","method":"tools/call","params":{"name":"web_read","arguments":{"url":"https://example.com"}}}'
    )

    assert response["ok"] is True
    assert response["result"]["items"][0]["text"] == "Hello"


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
