import json

from reachkit.core.formatting import (
    diagnostic_issues_to_json_text,
    diagnostic_issues_to_plain_text,
    to_json_text,
    to_plain_text,
)
from reachkit.core.models import DiagnosticIssue, RetrievedItem, SourceResult


def test_source_result_json_is_deterministic():
    result = SourceResult(
        source="web",
        url="https://example.com",
        title="Example",
        content_type="text/html",
        items=[
            RetrievedItem(
                title="Example",
                url="https://example.com",
                text="Hello world",
                metadata={"b": 2, "a": 1},
            )
        ],
        warnings=[],
    )

    text = to_json_text(result)

    assert text.endswith("\n")
    assert list(json.loads(text).keys()) == [
        "content_type",
        "items",
        "source",
        "title",
        "url",
        "warnings",
    ]
    assert '"a": 1' in text


def test_source_result_plain_text_renders_title_url_and_text():
    result = SourceResult(
        source="web",
        url="https://example.com",
        title="Example",
        content_type="text/html",
        items=[
            RetrievedItem(
                title="Item Title",
                url="https://example.com/item",
                text="First paragraph.",
            )
        ],
    )

    rendered = to_plain_text(result)

    assert "Example" in rendered
    assert "https://example.com/item" in rendered
    assert "First paragraph." in rendered


def test_diagnostic_formatting_supports_json_and_text():
    issues = [
        DiagnosticIssue(
            code="python_version",
            level="ok",
            message="Python version is valid.",
            required=True,
        )
    ]

    assert json.loads(diagnostic_issues_to_json_text(issues)) == {
        "issues": [
            {
                "code": "python_version",
                "level": "ok",
                "message": "Python version is valid.",
                "metadata": {},
                "required": True,
            }
        ]
    }
    assert "python_version" in diagnostic_issues_to_plain_text(issues)
