from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any

from reachkit.core.models import DiagnosticIssue, SourceResult


def source_result_to_dict(result: SourceResult) -> dict[str, Any]:
    return asdict(result)


def diagnostic_issue_to_dict(issue: DiagnosticIssue) -> dict[str, Any]:
    return asdict(issue)


def to_json_text(result: SourceResult) -> str:
    return json.dumps(source_result_to_dict(result), ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def to_plain_text(result: SourceResult) -> str:
    lines: list[str] = []
    if result.title:
        lines.append(result.title)
    if result.url:
        lines.append(result.url)
    if result.content_type:
        lines.append(f"Content-Type: {result.content_type}")

    for index, item in enumerate(result.items, start=1):
        if lines:
            lines.append("")
        heading = item.title or f"Item {index}"
        lines.append(heading)
        if item.url:
            lines.append(item.url)
        if item.text:
            lines.append(item.text)

    for warning in result.warnings:
        if lines:
            lines.append("")
        lines.append(f"Warning: {warning}")

    return "\n".join(lines).rstrip() + "\n"


def diagnostic_issues_to_json_text(issues: list[DiagnosticIssue]) -> str:
    payload = {"issues": [diagnostic_issue_to_dict(issue) for issue in issues]}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def diagnostic_issues_to_plain_text(issues: list[DiagnosticIssue]) -> str:
    lines = [f"[{issue.level}] {issue.code}: {issue.message}" for issue in issues]
    return "\n".join(lines).rstrip() + "\n"
