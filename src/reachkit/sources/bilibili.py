from __future__ import annotations

from collections.abc import Callable
import json
import re
from urllib.parse import urlencode, urlparse

from reachkit.core.errors import InputError, ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text

FetchText = Callable[..., HttpResponse]


def parse_video_ref(value: str) -> tuple[str, str]:
    candidate = value.strip()
    if not candidate:
        raise InputError("Bilibili video id is required")
    bvid = _find_bvid(candidate)
    if bvid:
        return "bvid", bvid
    aid = _find_aid(candidate)
    if aid:
        return "aid", aid
    raise InputError("Bilibili video id could not be found")


def parse_bvid(value: str) -> str:
    kind, video_id = parse_video_ref(value)
    if kind != "bvid":
        raise InputError("Bilibili BV id could not be found")
    return video_id


def _find_bvid(value: str) -> str | None:
    candidate = value.strip()
    if candidate.startswith("BV"):
        return candidate.rstrip("/")
    parsed = urlparse(candidate)
    parts = [part for part in parsed.path.split("/") if part]
    for part in parts:
        if part.startswith("BV"):
            return part.rstrip("/")
    match = re.search(r"(BV[0-9A-Za-z]+)", candidate)
    if match:
        return match.group(1)
    return None


def _find_aid(value: str) -> str | None:
    candidate = value.strip()
    if candidate.isdigit():
        return candidate
    if candidate.lower().startswith("av") and candidate[2:].isdigit():
        return candidate[2:]
    parsed = urlparse(candidate)
    parts = [part for part in parsed.path.split("/") if part]
    for part in parts:
        if part.lower().startswith("av") and part[2:].isdigit():
            return part[2:]
    match = re.search(r"(?:^|/)av(\d+)", candidate, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return None


class BilibiliVideoReader:
    name = "bilibili"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(self, video: str) -> SourceResult:
        ref_kind, video_id = parse_video_ref(video)
        url = "https://api.bilibili.com/x/web-interface/view?" + urlencode({ref_kind: video_id})
        active_fetcher = self._fetcher or fetch_text
        response = active_fetcher(url)
        payload = self._load_json(response)
        if not isinstance(payload, dict):
            raise ParseError("Bilibili response was not an object")
        if payload.get("code") != 0:
            message = payload.get("message") or "Bilibili request failed"
            raise ParseError(str(message))
        data = payload.get("data")
        if not isinstance(data, dict):
            raise ParseError("Bilibili response did not contain video data")
        result_bvid = str(data.get("bvid") or "") or (video_id if ref_kind == "bvid" else "")
        result_aid = data.get("aid") or (int(video_id) if ref_kind == "aid" and video_id.isdigit() else None)
        title = str(data.get("title") or result_bvid or result_aid or video_id)
        page_url = f"https://www.bilibili.com/video/{result_bvid}" if result_bvid else f"https://www.bilibili.com/video/av{result_aid}"
        owner = data.get("owner") if isinstance(data.get("owner"), dict) else {}
        stat = data.get("stat") if isinstance(data.get("stat"), dict) else {}
        lines = [title]
        description = data.get("desc")
        if description:
            lines.append(str(description))
        if owner.get("name"):
            lines.append(f"creator: {owner.get('name')}")
        if data.get("duration") is not None:
            lines.append(f"duration: {data.get('duration')}")
        if stat.get("view") is not None:
            lines.append(f"views: {stat.get('view')}")
        if stat.get("like") is not None:
            lines.append(f"likes: {stat.get('like')}")
        metadata = {
            "bvid": result_bvid or None,
            "aid": result_aid,
            "duration": data.get("duration"),
            "owner": owner,
            "stat": stat,
        }
        item = RetrievedItem(title=title, url=page_url, text=compact_text("\n".join(lines)), metadata=metadata)
        return SourceResult(self.name, page_url, title, response.headers.get("Content-Type"), [item], [])

    def _load_json(self, response: HttpResponse):
        try:
            return json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise ParseError("Bilibili response was not valid JSON") from exc
