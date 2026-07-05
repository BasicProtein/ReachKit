from __future__ import annotations

import json

from reachkit.cli import app
from reachkit.setup.executor import execute_install_plan
from reachkit.setup.planner import build_setup_plan
from reachkit.setup.uninstall import remove_reachkit_state


def test_setup_plan_contains_config_and_optional_guidance(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("REACHKIT_CONFIG", str(tmp_path / "config.toml"))

    exit_code = app.main(["setup", "plan", "--format", "json"])

    payload = json.loads(capsys.readouterr().out)
    kinds = {action["kind"] for action in payload["actions"]}
    assert exit_code == 0
    assert {"config_file", "python_extra", "manual_step"} <= kinds
    assert any("browser" in action["name"] for action in payload["actions"])


def test_setup_install_dry_run_does_not_create_config(tmp_path, monkeypatch, capsys):
    config_file = tmp_path / "config.toml"
    monkeypatch.setenv("REACHKIT_CONFIG", str(config_file))

    exit_code = app.main(["setup", "install", "--dry-run"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "dry-run" in output
    assert not config_file.exists()


def test_setup_install_safe_does_not_create_config(tmp_path, monkeypatch, capsys):
    config_file = tmp_path / "config.toml"
    monkeypatch.setenv("REACHKIT_CONFIG", str(config_file))

    exit_code = app.main(["setup", "install", "--safe"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "manual" in output.lower()
    assert not config_file.exists()


def test_setup_install_creates_config_file(tmp_path, monkeypatch):
    config_file = tmp_path / "config.toml"
    monkeypatch.setenv("REACHKIT_CONFIG", str(config_file))

    exit_code = app.main(["setup", "install"])

    assert exit_code == 0
    assert config_file.exists()
    assert "[auth.github]" in config_file.read_text(encoding="utf-8")


def test_setup_remove_preserves_config_without_purge(tmp_path, monkeypatch, capsys):
    config_file = tmp_path / "config.toml"
    config_file.write_text("[auth.github]\ntoken_env = \"GITHUB_TOKEN\"\n", encoding="utf-8")
    monkeypatch.setenv("REACHKIT_CONFIG", str(config_file))

    exit_code = app.main(["setup", "remove"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "kept" in output
    assert config_file.exists()


def test_setup_remove_purge_deletes_only_config_file(tmp_path, monkeypatch):
    config_file = tmp_path / ".reachkit" / "config.toml"
    sibling_file = tmp_path / ".reachkit" / "notes.txt"
    config_file.parent.mkdir()
    config_file.write_text("[auth.github]\ntoken_env = \"GITHUB_TOKEN\"\n", encoding="utf-8")
    sibling_file.write_text("keep", encoding="utf-8")
    monkeypatch.setenv("REACHKIT_CONFIG", str(config_file))

    exit_code = app.main(["setup", "remove", "--purge"])

    assert exit_code == 0
    assert not config_file.exists()
    assert sibling_file.exists()


def test_execute_install_plan_reports_actions_without_system_install(tmp_path):
    config_file = tmp_path / "config.toml"
    plan = build_setup_plan(config_file=config_file)

    result = execute_install_plan(plan)

    assert config_file.exists()
    assert any(item.action.kind == "config_file" and item.executed for item in result.items)
    assert all(not item.executed for item in result.items if item.action.kind == "python_extra")


def test_remove_reachkit_state_purge_only_removes_config_file(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("[auth.github]\ntoken_env = \"GITHUB_TOKEN\"\n", encoding="utf-8")

    result = remove_reachkit_state(config_file=config_file, purge=True)

    assert result.purged is True
    assert not config_file.exists()
