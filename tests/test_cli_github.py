import json

from reachkit.cli import app
from reachkit.core.models import RetrievedItem, SourceResult


class StubGitHubReader:
    def __init__(self):
        self.read_calls = []
        self.search_calls = []

    def read(self, **kwargs):
        self.read_calls.append(kwargs)
        return SourceResult(
            source="github",
            url="https://github.com/reachkit/demo",
            title=kwargs["repo"],
            content_type="application/json",
            items=[
                RetrievedItem(
                    title=kwargs["repo"],
                    url="https://github.com/reachkit/demo",
                    text="Repository text",
                    metadata={},
                )
            ],
        )

    def search(self, query, limit):
        self.search_calls.append({"query": query, "limit": limit})
        return SourceResult(
            source="github",
            url="https://api.github.com/search/repositories",
            title=f"GitHub search: {query}",
            content_type="application/json",
            items=[
                RetrievedItem(
                    title="reachkit/demo",
                    url="https://github.com/reachkit/demo",
                    text="Repository text",
                    metadata={},
                )
            ],
        )


def test_read_github_outputs_json(monkeypatch, capsys):
    reader = StubGitHubReader()
    from reachkit.cli.commands import read

    monkeypatch.setattr(read, "GitHubReader", lambda: reader)

    exit_code = app.main(["read", "github", "reachkit/demo", "--path", "README.md", "--ref", "main", "--format", "json"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["title"] == "reachkit/demo"
    assert reader.read_calls == [{"repo": "reachkit/demo", "path": "README.md", "ref": "main"}]


def test_search_github_outputs_text(monkeypatch, capsys):
    reader = StubGitHubReader()
    from reachkit.cli.commands import search

    monkeypatch.setattr(search, "GitHubReader", lambda: reader)

    exit_code = app.main(["search", "github", "agent tools", "--limit", "3"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "reachkit/demo" in captured.out
    assert reader.search_calls == [{"query": "agent tools", "limit": 3}]


def test_read_github_text_handles_unicode(monkeypatch, capsys):
    class UnicodeReader(StubGitHubReader):
        def read(self, **kwargs):
            return SourceResult(
                source="github",
                url="https://github.com/reachkit/demo",
                title=kwargs["repo"],
                content_type="application/json",
                items=[
                    RetrievedItem(
                        title="README.md",
                        url="https://github.com/reachkit/demo",
                        text="ReachKit café ©",
                        metadata={},
                    )
                ],
            )

    from reachkit.cli.commands import read

    monkeypatch.setattr(read, "GitHubReader", lambda: UnicodeReader())

    exit_code = app.main(["read", "github", "reachkit/demo"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "©" in output
    assert "café" in output
