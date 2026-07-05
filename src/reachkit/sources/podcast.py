from __future__ import annotations

from collections.abc import Callable
import xml.etree.ElementTree as ET

from reachkit.core.errors import ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text
from reachkit.runtime.limits import DEFAULT_LIMIT, MAX_LIMIT

FetchText = Callable[..., HttpResponse]


class PodcastReader:
    name = "podcast"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(self, url: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        response = (self._fetcher or fetch_text)(url)
        try:
            root = ET.fromstring(response.body)
        except ET.ParseError as exc:
            raise ParseError("Podcast feed was not valid XML") from exc
        channel = root.find("channel")
        if channel is None:
            raise ParseError("Podcast feed did not contain a channel")
        title = _text(channel, "title") or "Podcast feed"
        feed_link = _text(channel, "link") or response.url
        items: list[RetrievedItem] = []
        for element in channel.findall("item")[:active_limit]:
            item_title = _text(element, "title") or "Podcast episode"
            item_url = _text(element, "link")
            description = _text(element, "description")
            enclosure = element.find("enclosure")
            audio_url = enclosure.attrib.get("url") if enclosure is not None else None
            lines = [item_title]
            if description:
                lines.append(description)
            if audio_url:
                lines.append(f"audio: {audio_url}")
            items.append(
                RetrievedItem(
                    title=item_title,
                    url=item_url,
                    text=compact_text("\n".join(lines)),
                    metadata={"audio_url": audio_url, "audio_type": enclosure.attrib.get("type") if enclosure is not None else None},
                )
            )
        return SourceResult(self.name, feed_link, title, response.headers.get("Content-Type"), items, [])


def _text(element: ET.Element, name: str) -> str | None:
    child = element.find(name)
    if child is None or child.text is None:
        return None
    value = child.text.strip()
    return value or None
