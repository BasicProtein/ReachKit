from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reachkit.config.paths import config_path
from reachkit.core.errors import ConfigError


@dataclass(frozen=True)
class RemoveResult:
    purged: bool
    config_file: Path
    removed: list[Path]
    kept: list[Path]


def remove_reachkit_state(config_file: str | Path | None = None, purge: bool = False) -> RemoveResult:
    active_config = Path(config_file) if config_file is not None else config_path()
    removed: list[Path] = []
    kept: list[Path] = []
    if purge:
        try:
            if active_config.exists():
                active_config.unlink()
                removed.append(active_config)
        except OSError as exc:
            raise ConfigError("ReachKit setup could not remove the config file") from exc
    else:
        if active_config.exists():
            kept.append(active_config)
    return RemoveResult(purged=purge, config_file=active_config, removed=removed, kept=kept)
