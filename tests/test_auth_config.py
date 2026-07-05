from __future__ import annotations

import json

from reachkit.cli import app
from reachkit.config.settings import load_settings


def test_auth_set_github_stores_env_name_without_token_value(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    monkeypatch.setenv("REACHKIT_CONFIG", str(config_file))
    monkeypatch.setenv("GITHUB_TOKEN", "secret-token-value")

    exit_code = app.main(["auth", "set", "github", "--token-env", "GITHUB_TOKEN"])

    text = config_file.read_text(encoding="utf-8")
    assert exit_code == 0
    assert 'token_env = "GITHUB_TOKEN"' in text
    assert "secret-token-value" not in text


def test_auth_set_browser_validates_storage_state_file(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    storage_state = tmp_path / "state.json"
    storage_state.write_text(json.dumps({"cookies": [], "origins": []}), encoding="utf-8")
    monkeypatch.setenv("REACHKIT_CONFIG", str(config_file))

    exit_code = app.main(["auth", "set", "browser", "--storage-state", str(storage_state)])

    assert exit_code == 0
    assert load_settings(config_file)["auth"]["browser"]["storage_state"] == str(storage_state)


def test_auth_set_web_validates_cookie_file(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    cookie_file = tmp_path / "cookies.json"
    cookie_file.write_text(json.dumps([{"name": "session", "value": "abc"}]), encoding="utf-8")
    monkeypatch.setenv("REACHKIT_CONFIG", str(config_file))

    exit_code = app.main(["auth", "set", "web", "--cookie-file", str(cookie_file)])

    assert exit_code == 0
    assert load_settings(config_file)["auth"]["web"]["cookie_file"] == str(cookie_file)


def test_auth_set_rejects_missing_storage_state(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("REACHKIT_CONFIG", str(tmp_path / "config.toml"))

    exit_code = app.main(["auth", "set", "browser", "--storage-state", str(tmp_path / "missing.json")])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "storage-state" in captured.err


def test_auth_status_json_reports_config_without_secret_values(tmp_path, monkeypatch, capsys):
    config_file = tmp_path / "config.toml"
    monkeypatch.setenv("REACHKIT_CONFIG", str(config_file))
    monkeypatch.setenv("GITHUB_TOKEN", "secret-token-value")
    app.main(["auth", "set", "github", "--token-env", "GITHUB_TOKEN"])
    capsys.readouterr()

    exit_code = app.main(["auth", "status", "--format", "json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert "secret-token-value" not in captured.out
    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["github_token"]["state"] == "configured"
    assert "facebook_token" in checks
    assert "instagram_token" in checks


def test_auth_status_text_mentions_explicit_file_paths(tmp_path, monkeypatch, capsys):
    config_file = tmp_path / "config.toml"
    cookie_file = tmp_path / "cookies.json"
    cookie_file.write_text(json.dumps([{"name": "session", "value": "abc"}]), encoding="utf-8")
    monkeypatch.setenv("REACHKIT_CONFIG", str(config_file))
    app.main(["auth", "set", "web", "--cookie-file", str(cookie_file)])
    capsys.readouterr()

    exit_code = app.main(["auth", "status"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "[configured] web_cookie_file" in output
    assert str(cookie_file) in output
