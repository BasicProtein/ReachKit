from __future__ import annotations

from collections.abc import Callable
import xml.etree.ElementTree as ET

from reachkit.core.errors import ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text
from reachkit.runtime.limits import DEFAULT_LIMIT, MAX_LIMIT

FetchText = Callable[..., HttpResponse]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _first_text(element: ET.Element, names: tuple[str, ...]) -> str | None:
    for child in list(element):
        if _local_name(child.tag) in names and child.text:
            return compact_text(child.text)
    return None


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(element) if _local_name(child.tag) == name]


class RssReader:
    name = "rss"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(self, url: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        active_fetcher = self._fetcher or fetch_text
        response = active_fetcher(url)
        try:
            root = ET.fromstring(response.body)
        except ET.ParseError as exc:
            raise ParseError("Feed XML could not be parsed") from exc

        root_name = _local_name(root.tag)
        if root_name == "rss" or root_name == "RDF":
            return self._read_rss(response, root, active_limit)
        if root_name == "feed":
            return self._read_atom(response, root, active_limit)
        raise ParseError("Feed root is not handled")

    def _read_rss(self, response: HttpResponse, root: ET.Element, limit: int) -> SourceResult:
        channel = next(iter(_children(root, "channel")), root)
        title = _first_text(channel, ("title",))
        items: list[RetrievedItem] = []
        for item in _children(channel, "item")[:limit]:
            item_title = _first_text(item, ("title",))
            item_url = _first_text(item, ("link",))
            text = _first_text(item, ("description", "summary")) or ""
            metadata = {"kind": "rss"}
            published = _first_text(item, ("pubDate", "published", "date"))
            if published:
                metadata["published"] = published
            items.append(RetrievedItem(title=item_title, url=item_url, text=text, metadata=metadata))
        warnings = [] if items else ["empty_feed"]
        return SourceResult(self.name, response.url, title, response.headers.get("Content-Type"), items, warnings)

    def _read_atom(self, response: HttpResponse, root: ET.Element, limit: int) -> SourceResult:
        title = _first_text(root, ("title",))
        items: list[RetrievedItem] = []
        for entry in _children(root, "entry")[:limit]:
            item_title = _first_text(entry, ("title",))
            item_url = None
            for child in list(entry):
                if _local_name(child.tag) == "link":
                    item_url = child.attrib.get("href") or compact_text(child.text or "") or None
                    break
            text = _first_text(entry, ("summary", "content")) or ""
            metadata = {"kind": "atom"}
            published = _first_text(entry, ("updated", "published"))
            if published:
                metadata["published"] = published
            items.append(RetrievedItem(title=item_title, url=item_url, text=text, metadata=metadata))
        warnings = [] if items else ["empty_feed"]
        return SourceResult(self.name, response.url, title, response.headers.get("Content-Type"), items, warnings)
