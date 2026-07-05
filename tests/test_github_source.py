from pathlib import Path

import pytest

from reachkit.core.errors import InputError, ParseError
from reachkit.runtime.http import HttpResponse
from reachkit.sources.github import GitHubReader, parse_repo_spec

FIXTURES = Path(__file__).parent / "fixtures"


class RecordingFetcher:
    def __init__(self, body: str):
        self.body = body
        self.calls = []

    def __call__(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "application/json"},
            body=self.body,
        )


def test_parse_repo_spec_accepts_owner_repo():
    assert parse_repo_spec("reachkit/demo") == ("reachkit", "demo")


def test_parse_repo_spec_rejects_other_shapes():
    with pytest.raises(InputError):
        parse_repo_spec("reachkit/demo/extra")


def test_github_reader_maps_repository_metadata():
    fetcher = RecordingFetcher((FIXTURES / "github-repo.json").read_text(encoding="utf-8"))
    reader = GitHubReader(fetcher=fetcher)

    result = reader.read_repo("reachkit", "demo")

    assert result.source == "github"
    assert result.title == "reachkit/demo"
    assert result.items[0].metadata == {
        "default_branch": "main",
        "stars": 7,
        "language": "Python",
    }
    assert fetcher.calls[0][0] == "https://api.github.com/repos/reachkit/demo"


def test_github_reader_decodes_file_content():
    fetcher = RecordingFetcher((FIXTURES / "github-file.json").read_text(encoding="utf-8"))
    reader = GitHubReader(fetcher=fetcher)

    result = reader.read_file("reachkit", "demo", "README.md", ref="main")

    assert result.items[0].title == "README.md"
    assert "Hello from fixture." in result.items[0].text
    assert fetcher.calls[0][0].endswith("/contents/README.md?ref=main")


def test_github_reader_rejects_directory_payload():
    fetcher = RecordingFetcher("[]")
    reader = GitHubReader(fetcher=fetcher)

    with pytest.raises(InputError):
        reader.read_file("reachkit", "demo", "docs")


def test_github_reader_rejects_binary_file():
    fetcher = RecordingFetcher('{"encoding":"base64","content":"AAE=","path":"bin.dat"}')
    reader = GitHubReader(fetcher=fetcher)

    with pytest.raises(ParseError):
        reader.read_file("reachkit", "demo", "bin.dat")


def test_github_reader_maps_search_results():
    fetcher = RecordingFetcher((FIXTURES / "github-search.json").read_text(encoding="utf-8"))
    reader = GitHubReader(fetcher=fetcher)

    result = reader.search_repositories("agent tools", limit=1)

    assert result.title == "GitHub search: agent tools"
    assert [item.title for item in result.items] == ["reachkit/demo"]
    assert "per_page=1" in fetcher.calls[0][0]
