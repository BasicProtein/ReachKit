import pytest

from reachkit.core.models import (
    DiagnosticIssue,
    GitHubRepoSummary,
    RetrievedItem,
    SourceResult,
)


def test_source_result_holds_retrieved_items():
    item = RetrievedItem(
        title="Example",
        url="https://example.com",
        text="Example text",
        metadata={"kind": "page"},
    )

    result = SourceResult(
        source="web",
        url="https://example.com",
        title="Example",
        content_type="text/html",
        items=[item],
        warnings=[],
    )

    assert result.items == [item]
    assert result.items[0].metadata == {"kind": "page"}


def test_diagnostic_issue_accepts_known_levels():
    issue = DiagnosticIssue(
        code="python_version",
        level="ok",
        message="Python version is valid.",
        required=True,
    )

    assert issue.required is True


def test_diagnostic_issue_rejects_unknown_level():
    with pytest.raises(ValueError):
        DiagnosticIssue(code="bad", level="notice", message="Bad level")


def test_github_repo_summary_defaults():
    summary = GitHubRepoSummary(
        full_name="owner/repo",
        url="https://github.com/owner/repo",
        description=None,
        default_branch="main",
    )

    assert summary.stars is None
    assert summary.language is None
