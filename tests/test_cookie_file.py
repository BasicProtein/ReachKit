from __future__ import annotations

import json

from reachkit.runtime.cookies import load_cookie_header


def test_load_cookie_header_reads_json_cookie_list(tmp_path):
    cookie_file = tmp_path / "cookies.json"
    cookie_file.write_text(
        json.dumps(
            [
                {"name": "session", "value": "abc123", "domain": "example.com"},
                {"name": "theme", "value": "dark", "domain": "example.com"},
            ]
        ),
        encoding="utf-8",
    )

    assert load_cookie_header(cookie_file) == "session=abc123; theme=dark"


def test_load_cookie_header_reads_storage_state_cookies(tmp_path):
    cookie_file = tmp_path / "storage-state.json"
    cookie_file.write_text(
        json.dumps(
            {
                "cookies": [
                    {"name": "session", "value": "abc123", "domain": "example.com"},
                    {"name": "locale", "value": "en", "domain": "example.com"},
                ],
                "origins": [],
            }
        ),
        encoding="utf-8",
    )

    assert load_cookie_header(cookie_file) == "session=abc123; locale=en"


def test_load_cookie_header_reads_netscape_cookie_file(tmp_path):
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text(
        "\n".join(
            [
                "# Netscape HTTP Cookie File",
                ".example.com\tTRUE\t/\tFALSE\t0\tsession\tabc123",
                ".example.com\tTRUE\t/\tFALSE\t0\ttheme\tdark",
            ]
        ),
        encoding="utf-8",
    )

    assert load_cookie_header(cookie_file) == "session=abc123; theme=dark"
