from __future__ import annotations

from reachkit.config.settings import load_settings, set_auth_value


def test_set_auth_value_creates_parent_directory_and_auth_section(tmp_path):
    config_file = tmp_path / "nested" / "config.toml"

    set_auth_value("github", "token_env", "GITHUB_TOKEN", path=config_file)

    assert load_settings(config_file)["auth"]["github"]["token_env"] == "GITHUB_TOKEN"


def test_set_auth_value_preserves_unrelated_sections(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('[features]\nkeep = true\n\n[auth.github]\ntoken_env = "OLD_TOKEN"\n', encoding="utf-8")

    set_auth_value("github", "token_env", "GITHUB_TOKEN", path=config_file)

    settings = load_settings(config_file)
    assert settings["features"]["keep"] is True
    assert settings["auth"]["github"]["token_env"] == "GITHUB_TOKEN"
