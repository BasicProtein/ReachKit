from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reachkit.config.paths import config_path
from reachkit.setup.actions import SetupAction


@dataclass(frozen=True)
class SetupPlan:
    actions: list[SetupAction]
    config_file: Path


def build_setup_plan(config_file: str | Path | None = None) -> SetupPlan:
    active_config = Path(config_file) if config_file is not None else config_path()
    actions = [
        SetupAction(
            kind="config_file",
            name="local_config",
            description=f"Create ReachKit config file at {active_config}",
            required=True,
            executable=True,
        ),
        SetupAction(
            kind="python_extra",
            name="browser_extra",
            description="Optional browser reader support can be installed with the browser extra",
            command=["python", "-m", "pip", "install", "reachkit[browser]"],
        ),
        SetupAction(
            kind="manual_step",
            name="github_token_env",
            description="Set GITHUB_TOKEN when authenticated GitHub API access is needed",
        ),
        SetupAction(
            kind="manual_step",
            name="x_token_env",
            description="Set X_BEARER_TOKEN when X API access is needed",
        ),
        SetupAction(
            kind="manual_step",
            name="xiaohongshu_app_env",
            description="Set XHS_APP_KEY and XHS_APP_SECRET for Xiaohongshu open API access",
        ),
        SetupAction(
            kind="manual_step",
            name="browser_storage_state",
            description="Configure a Playwright storage-state file only when rendered authenticated reads are required",
        ),
    ]
    return SetupPlan(actions=actions, config_file=active_config)


def default_config_text() -> str:
    return "\n".join(
        [
            "[auth.github]",
            'token_env = "GITHUB_TOKEN"',
            "",
            "[auth.x]",
            'token_env = "X_BEARER_TOKEN"',
            "",
            "[auth.xiaohongshu]",
            'app_key_env = "XHS_APP_KEY"',
            'app_secret_env = "XHS_APP_SECRET"',
            "",
            "[auth.browser]",
            'storage_state = ""',
            "",
            "[auth.web]",
            'cookie_file = ""',
            "",
        ]
    )
