from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

AuthState = Literal["configured", "missing", "invalid"]


@dataclass(frozen=True)
class AuthCheck:
    name: str
    state: AuthState
    message: str
    fix: str | None = None
