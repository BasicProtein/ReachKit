from __future__ import annotations

from html.parser import HTMLParser

from reachkit.normalization.text import compact_text

_HIDDEN_TAGS = {"script", "style", "noscript", "template"}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._hidden_depth = 0
        self._in_title = False
        self._title_parts: list[str] = []
        self._body_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        tag_name = tag.lower()
        if tag_name in _HIDDEN_TAGS:
            self._hidden_depth += 1
        elif tag_name == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        tag_name = tag.lower()
        if tag_name in _HIDDEN_TAGS and self._hidden_depth:
            self._hidden_depth -= 1
        elif tag_name == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._hidden_depth:
            return
        if self._in_title:
            self._title_parts.append(data)
            return
        self._body_parts.append(data)

    @property
    def title(self) -> str | None:
        value = compact_text(" ".join(self._title_parts))
        return value or None

    @property
    def text(self) -> str:
        return compact_text(" ".join(self._body_parts))


def html_to_text(html: str) -> tuple[str, str | None]:
    parser = _TextExtractor()
    parser.feed(html)
    parser.close()
    return parser.text, parser.title
