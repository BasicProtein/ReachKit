from io import StringIO
import json

from reachkit.cli import app


def test_serve_stdio_handles_single_request(monkeypatch):
    input_stream = StringIO('{"id":"1","method":"tools/list","params":{}}\n')
    output_stream = StringIO()

    monkeypatch.setattr("sys.stdin", input_stream)
    monkeypatch.setattr("sys.stdout", output_stream)

    exit_code = app.main(["serve", "stdio"])

    assert exit_code == 0
    assert json.loads(output_stream.getvalue())["ok"] is True
