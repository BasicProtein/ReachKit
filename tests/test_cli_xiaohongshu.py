from __future__ import annotations

import json

from reachkit.cli import app
from reachkit.core.models import RetrievedItem, SourceResult


def test_read_xiaohongshu_outputs_json(monkeypatch, capsys):
    calls = []

    class StubReader:
        def read(self, **kwargs):
            calls.append(kwargs)
            return SourceResult(
                source="xiaohongshu",
                url="https://edith.xiaohongshu.com/api/open/test",
                title="Xiaohongshu API: /api/open/test",
                content_type="application/json",
                items=[RetrievedItem(title="Sample note", url=None, text="Useful public content", metadata={})],
                warnings=[],
            )

    monkeypatch.setattr("reachkit.cli.commands.read.XiaohongshuApiReader", StubReader)

    exit_code = app.main(
        [
            "read",
            "xiaohongshu",
            "/api/open/test",
            "--param",
            "note_id=abc",
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)["source"] == "xiaohongshu"
    assert calls[0]["path"] == "/api/open/test"
    assert calls[0]["query"] == {"note_id": "abc"}


def test_read_xiaohongshu_rejects_invalid_param(capsys):
    exit_code = app.main(["read", "xiaohongshu", "/api/open/test", "--param", "bad"])

    assert exit_code == 2
