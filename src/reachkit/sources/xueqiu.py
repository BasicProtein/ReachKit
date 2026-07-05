from __future__ import annotations

from collections.abc import Callable
import json
from urllib.parse import urlencode

from reachkit.core.errors import ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text
from reachkit.runtime.limits import DEFAULT_LIMIT, MAX_LIMIT

FetchText = Callable[..., HttpResponse]


class XueqiuReader:
    name = "xueqiu"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(self, target: str) -> SourceResult:
        return self.quote(target)

    def quote(self, symbol: str) -> SourceResult:
        url = "https://stock.xueqiu.com/v5/stock/quote.json?" + urlencode({"symbol": symbol})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        records = data.get("data") if isinstance(data, dict) else None
        record = records[0] if isinstance(records, list) and records else records if isinstance(records, dict) else {}
        if not isinstance(record, dict):
            raise ParseError("Xueqiu quote response did not contain quote data")
        item = _stock_item(record)
        return SourceResult(self.name, url, item.title, response.headers.get("Content-Type"), [item], [])

    def search(self, query: str, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        url = "https://xueqiu.com/query/v1/stock/search.json?" + urlencode({"q": query, "count": active_limit})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        records = data.get("data") if isinstance(data, dict) else []
        items = [_stock_item(record) for record in list(records or [])[:active_limit] if isinstance(record, dict)]
        return SourceResult(self.name, url, f"Xueqiu search: {query}", response.headers.get("Content-Type"), items, [])

    def hot(self, limit: int = DEFAULT_LIMIT) -> SourceResult:
        active_limit = min(max(1, limit), MAX_LIMIT)
        url = "https://xueqiu.com/statuses/hot/listV2.json?" + urlencode({"size": active_limit})
        response = (self._fetcher or fetch_text)(url)
        data = self._load_json(response)
        container = data.get("data") if isinstance(data, dict) else {}
        records = container.get("items") if isinstance(container, dict) else []
        items: list[RetrievedItem] = []
        for record in list(records or [])[:active_limit]:
            if not isinstance(record, dict):
                continue
            title = str(record.get("title") or record.get("symbol") or "Xueqiu item")
            items.append(RetrievedItem(title=title, url=record.get("target"), text=compact_text(title), metadata=record))
        return SourceResult(self.name, url, "Xueqiu hot", response.headers.get("Content-Type"), items, [])

    def _load_json(self, response: HttpResponse):
        try:
            return json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise ParseError("Xueqiu response was not valid JSON") from exc


def _stock_item(record: dict) -> RetrievedItem:
    symbol = record.get("symbol") or record.get("code")
    title = str(record.get("name") or symbol or "Xueqiu stock")
    lines = [title]
    if symbol:
        lines.append(f"symbol: {symbol}")
    if record.get("current") is not None:
        lines.append(f"price: {record.get('current')}")
    return RetrievedItem(title=title, url=None, text=compact_text("\n".join(lines)), metadata={"symbol": symbol, **record})
