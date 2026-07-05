from __future__ import annotations

from dataclasses import dataclass

from reachkit.core.errors import ConfigError
from reachkit.setup.actions import SetupAction
from reachkit.setup.planner import SetupPlan, default_config_text


@dataclass(frozen=True)
class SetupActionResult:
    action: SetupAction
    executed: bool
    message: str


@dataclass(frozen=True)
class SetupExecutionResult:
    items: list[SetupActionResult]


def execute_install_plan(plan: SetupPlan, dry_run: bool = False, safe: bool = False) -> SetupExecutionResult:
    results: list[SetupActionResult] = []
    for action in plan.actions:
        if dry_run:
            results.append(SetupActionResult(action=action, executed=False, message="dry-run"))
            continue
        if safe:
            results.append(SetupActionResult(action=action, executed=False, message="manual step"))
            continue
        if action.kind == "config_file":
            _ensure_config(plan)
            results.append(SetupActionResult(action=action, executed=True, message="created or kept"))
        else:
            results.append(SetupActionResult(action=action, executed=False, message="guidance only"))
    return SetupExecutionResult(items=results)


def _ensure_config(plan: SetupPlan) -> None:
    try:
        plan.config_file.parent.mkdir(parents=True, exist_ok=True)
        if not plan.config_file.exists():
            plan.config_file.write_text(default_config_text(), encoding="utf-8")
    except OSError as exc:
        raise ConfigError("ReachKit setup could not create the config file") from exc
