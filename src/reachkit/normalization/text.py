from __future__ import annotations

import re


def truncate_text(text: str, max_chars: int | None = None) -> str:
    if max_chars is None or len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return "." * max_chars
    return text[: max_chars - 3].rstrip() + "..."


def compact_text(text: str, max_chars: int | None = None) -> str:
    compacted = re.sub(r"\s+", " ", text).strip()
    return truncate_text(compacted, max_chars)
