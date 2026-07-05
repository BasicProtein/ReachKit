from __future__ import annotations

import json

from reachkit.cli import app
from reachkit.channels.diagnostics import diagnose_channel, diagnose_channels
from reachkit.channels.registry import default_channel_registry


def test_default_channel_registry_lists_current_platforms():
    registry = default_channel_registry()

    assert registry.names() == [
        "web",
        "rss",
        "github",
        "youtube",
        "x",
        "bilibili",
        "xiaohongshu",
        "browser",
        "v2ex",
        "podcast",
        "reddit",
        "linkedin",
        "xueqiu",
        "facebook",
        "instagram",
    ]
    github = registry.get("github")
    assert [capability.kind for capability in github.capabilities] == ["read", "search", "metadata", "comments"]


def test_channel_doctor_reports_provider_status_without_env(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("REACHKIT_WEB_SEARCH_URL", raising=False)
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    monkeypatch.delenv("XHS_APP_KEY", raising=False)
    monkeypatch.delenv("XHS_APP_SECRET", raising=False)

    status = diagnose_channel("x")

    assert status.name == "x"
    assert status.state == "needs_config"
    assert status.selected_provider is None
    assert status.providers[0].state == "needs_config"
    assert status.providers[0].access == "official_api"
    assert "X_BEARER_TOKEN" in (status.providers[0].fix or "")


def test_web_channel_reports_search_endpoint_configuration(monkeypatch):
    monkeypatch.delenv("REACHKIT_WEB_SEARCH_URL", raising=False)

    missing = diagnose_channel("web")
    assert any(provider.name == "search_endpoint" and provider.state == "needs_config" for provider in missing.providers)
    assert any(capability.kind == "search" and capability.requires_auth for capability in missing.capabilities)

    monkeypatch.setenv("REACHKIT_WEB_SEARCH_URL", "https://search.example/api")
    ready = diagnose_channel("web")
    provider = next(provider for provider in ready.providers if provider.name == "search_endpoint")
    assert provider.state == "available"


def test_youtube_channel_reports_metadata_api_configuration(monkeypatch):
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)

    missing = diagnose_channel("youtube")
    assert any(provider.name == "metadata_api" and provider.state == "needs_config" for provider in missing.providers)

    monkeypatch.setenv("YOUTUBE_API_KEY", "key")
    ready = diagnose_channel("youtube")
    provider = next(provider for provider in ready.providers if provider.name == "metadata_api")
    assert provider.state == "available"


def test_v2ex_channel_describes_topic_replies():
    channel = default_channel_registry().get("v2ex")

    comments = next(capability for capability in channel.capabilities if capability.kind == "comments")
    assert "replies" in comments.label.lower()


def test_diagnose_channels_can_filter_to_one_channel():
    statuses = diagnose_channels(name="github")

    assert [status.name for status in statuses] == ["github"]
    assert statuses[0].selected_provider == "public_api"


def test_channels_list_cli_outputs_text(capsys):
    exit_code = app.main(["channels", "list"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "github" in output
    assert "read, search, metadata" in output


def test_channels_doctor_cli_outputs_json(monkeypatch, capsys):
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_BEARER_TOKEN", raising=False)

    exit_code = app.main(["channels", "doctor", "x", "--format", "json"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["channels"][0]["name"] == "x"
    assert payload["channels"][0]["state"] == "needs_config"


def test_channels_doctor_cli_without_channel_outputs_all_json(capsys):
    exit_code = app.main(["channels", "doctor", "--format", "json"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert len(payload["channels"]) >= 15
    assert {channel["name"] for channel in payload["channels"]} >= {
        "web",
        "github",
        "x",
        "v2ex",
        "podcast",
        "reddit",
        "linkedin",
        "xueqiu",
        "facebook",
        "instagram",
    }
