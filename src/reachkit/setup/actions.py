from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ActionKind = Literal["python_extra", "config_file", "manual_step", "check_command"]


@dataclass(frozen=True)
class SetupAction:
    kind: ActionKind
    name: str
    description: str
    command: list[str] | None = None
    required: bool = False
    executable: bool = False
