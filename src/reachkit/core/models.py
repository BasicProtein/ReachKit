from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RetrievedItem:
    title: str | None
    url: str | None
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SourceResult:
    source: str
    url: str | None
    title: str | None
    content_type: str | None
    items: list[RetrievedItem]
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DiagnosticIssue:
    code: str
    level: str
    message: str
    required: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.level not in {"ok", "warning", "error"}:
            raise ValueError("Diagnostic level must be ok, warning, or error")


@dataclass(frozen=True)
class GitHubRepoSummary:
    full_name: str
    url: str
    description: str | None
    default_branch: str | None
    stars: int | None = None
    language: str | None = None
