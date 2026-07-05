from __future__ import annotations

import os
from pathlib import Path


CONFIG_ENV_VAR = "REACHKIT_CONFIG"


def config_path() -> Path:
    override = os.environ.get(CONFIG_ENV_VAR)
    if override:
        return Path(override).expanduser()
    return Path.home() / ".reachkit" / "config.toml"
