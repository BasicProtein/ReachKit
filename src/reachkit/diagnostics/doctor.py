from __future__ import annotations

import os
import ssl
import sys
import tempfile
from pathlib import Path

from reachkit.core.models import DiagnosticIssue
from reachkit.runtime.http import fetch_text


def check_python_version() -> DiagnosticIssue:
    if sys.version_info >= (3, 11):
        return DiagnosticIssue("python_version", "ok", "Python version is valid.", required=True)
    return DiagnosticIssue("python_version", "error", "Python 3.11 or newer is required.", required=True)


def check_utf8_io() -> DiagnosticIssue:
    try:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "utf8.txt"
            path.write_text("ReachKit ✓", encoding="utf-8")
            if path.read_text(encoding="utf-8") != "ReachKit ✓":
                raise OSError("Round trip mismatch")
        return DiagnosticIssue("utf8_io", "ok", "UTF-8 file I/O is available.", required=True)
    except OSError:
        return DiagnosticIssue("utf8_io", "error", "UTF-8 file I/O failed.", required=True)


def check_https_runtime() -> DiagnosticIssue:
    if ssl.OPENSSL_VERSION:
        return DiagnosticIssue("https_runtime", "ok", "HTTPS support is available.", required=True)
    return DiagnosticIssue("https_runtime", "error", "HTTPS is unavailable.", required=True)


def check_github_token() -> DiagnosticIssue:
    if os.environ.get("GITHUB_TOKEN"):
        return DiagnosticIssue("github_token", "ok", "GitHub token is configured.")
    return DiagnosticIssue("github_token", "warning", "GitHub token is not configured.")


def check_x_token() -> DiagnosticIssue:
    if os.environ.get("X_BEARER_TOKEN") or os.environ.get("TWITTER_BEARER_TOKEN"):
        return DiagnosticIssue("x_token", "ok", "X API token is configured.")
    return DiagnosticIssue("x_token", "warning", "X API token is not configured.")


def check_xhs_credentials() -> DiagnosticIssue:
    if os.environ.get("XHS_APP_KEY") and os.environ.get("XHS_APP_SECRET"):
        return DiagnosticIssue("xhs_credentials", "ok", "Xiaohongshu API credentials are configured.")
    return DiagnosticIssue("xhs_credentials", "warning", "Xiaohongshu API credentials are not configured.")


def check_network_example() -> DiagnosticIssue:
    try:
        fetch_text("https://example.com")
        return DiagnosticIssue("network_example", "ok", "Example network request succeeded.")
    except Exception:
        return DiagnosticIssue("network_example", "warning", "Example network request failed.")


def run_doctor(include_network: bool = True) -> list[DiagnosticIssue]:
    issues = [
        check_python_version(),
        check_utf8_io(),
        check_https_runtime(),
        check_github_token(),
        check_x_token(),
        check_xhs_credentials(),
    ]
    if include_network:
        issues.append(check_network_example())
    return issues


def required_checks_failed(issues: list[DiagnosticIssue]) -> bool:
    return any(issue.required and issue.level == "error" for issue in issues)
