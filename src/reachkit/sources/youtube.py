from __future__ import annotations

from collections.abc import Callable
import html
from urllib.parse import parse_qs, urlencode, urlparse
import xml.etree.ElementTree as ET
import os

from reachkit.core.errors import InputError, ParseError
from reachkit.core.models import RetrievedItem, SourceResult
from reachkit.normalization.text import compact_text
from reachkit.runtime.http import HttpResponse, fetch_text

FetchText = Callable[..., HttpResponse]


def parse_video_id(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        raise InputError("YouTube video id is required")
    parsed = urlparse(candidate)
    if not parsed.scheme:
        return _validate_video_id(candidate)
    host = parsed.netloc.lower()
    if host.endswith("youtu.be"):
        return _validate_video_id(parsed.path.strip("/").split("/", 1)[0])
    if "youtube.com" in host:
        query_id = parse_qs(parsed.query).get("v", [""])[0]
        if query_id:
            return _validate_video_id(query_id)
        parts = [part for part in parsed.path.split("/") if part]
        for marker in ("shorts", "embed"):
            if marker in parts:
                index = parts.index(marker)
                if index + 1 < len(parts):
                    return _validate_video_id(parts[index + 1])
    raise InputError("YouTube video id could not be found")


def _validate_video_id(video_id: str) -> str:
    if not video_id or any(char.isspace() for char in video_id):
        raise InputError("YouTube video id is not valid")
    return video_id


class YouTubeTranscriptReader:
    name = "youtube"

    def __init__(self, fetcher: FetchText | None = None) -> None:
        self._fetcher = fetcher

    def read(self, video: str, lang: str = "en", max_chars: int | None = None) -> SourceResult:
        video_id = parse_video_id(video)
        active_fetcher = self._fetcher or fetch_text
        list_url = "https://video.google.com/timedtext?" + urlencode({"type": "list", "v": video_id})
        list_response = active_fetcher(list_url)
        selected_lang = self._select_language(list_response.body, lang)
        transcript_url = "https://video.google.com/timedtext?" + urlencode({"v": video_id, "lang": selected_lang})
        transcript_response = active_fetcher(transcript_url)
        text = self._parse_transcript(transcript_response.body, max_chars=max_chars)
        title = f"YouTube transcript: {video_id}"
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        item = RetrievedItem(
            title=title,
            url=watch_url,
            text=text,
            metadata={"video_id": video_id, "language": selected_lang},
        )
        return SourceResult(
            self.name,
            watch_url,
            title,
            transcript_response.headers.get("Content-Type"),
            [item],
            [],
        )

    def _select_language(self, body: str, preferred: str) -> str:
        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            raise ParseError("YouTube transcript list was not valid XML") from exc
        tracks = [element.attrib for element in root.findall("track")]
        if not tracks:
            raise ParseError("YouTube transcript is not available")
        for track in tracks:
            if track.get("lang_code") == preferred:
                return preferred
        fallback = tracks[0].get("lang_code")
        if not fallback:
            raise ParseError("YouTube transcript language was missing")
        return fallback

    def _parse_transcript(self, body: str, max_chars: int | None = None) -> str:
        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            raise ParseError("YouTube transcript was not valid XML") from exc
        chunks: list[str] = []
        for element in root.findall("text"):
            if element.text:
                chunks.append(html.unescape(element.text))
        text = compact_text(" ".join(chunks), max_chars=max_chars)
        if not text:
            raise ParseError("YouTube transcript was empty")
        return text


class YouTubeSearchReader:
    name = "youtube"

    def __init__(self, fetcher: FetchText | None = None, api_key: str | None = None) -> None:
        self._fetcher = fetcher
        self._api_key = api_key

    def search(self, query: str, limit: int = 10) -> SourceResult:
        api_key = self._api_key or os.environ.get("YOUTUBE_API_KEY")
        if not api_key:
            raise InputError("YOUTUBE_API_KEY is required for YouTube search")
        active_limit = max(1, min(limit, 25))
        params = {
            "part": "snippet",
            "type": "video",
            "q": query,
            "maxResults": active_limit,
            "key": api_key,
        }
        url = "https://www.googleapis.com/youtube/v3/search?" + urlencode(params)
        response = (self._fetcher or fetch_text)(url)
        try:
            data = json_loads(response.body)
        except ValueError as exc:
            raise ParseError("YouTube search response was not valid JSON") from exc
        items: list[RetrievedItem] = []
        for record in list(data.get("items") or [])[:active_limit]:
            if not isinstance(record, dict):
                continue
            snippet = record.get("snippet") if isinstance(record.get("snippet"), dict) else {}
            video_id = record.get("id", {}).get("videoId") if isinstance(record.get("id"), dict) else None
            title = html.unescape(str(snippet.get("title") or video_id or "YouTube video"))
            video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else None
            lines = [title]
            if snippet.get("description"):
                lines.append(str(snippet.get("description")))
            if snippet.get("channelTitle"):
                lines.append(f"channel: {snippet.get('channelTitle')}")
            items.append(
                RetrievedItem(
                    title=title,
                    url=video_url,
                    text=compact_text("\n".join(lines)),
                    metadata={
                        "video_id": video_id,
                        "channel": snippet.get("channelTitle"),
                        "published_at": snippet.get("publishedAt"),
                    },
                )
            )
        return SourceResult(self.name, url, f"YouTube search: {query}", response.headers.get("Content-Type"), items, [])


class YouTubeMetadataReader:
    name = "youtube"

    def __init__(self, fetcher: FetchText | None = None, api_key: str | None = None) -> None:
        self._fetcher = fetcher
        self._api_key = api_key

    def read(self, video: str) -> SourceResult:
        video_id = parse_video_id(video)
        api_key = self._api_key or os.environ.get("YOUTUBE_API_KEY")
        if not api_key:
            raise InputError("YOUTUBE_API_KEY is required for YouTube metadata")
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
            "key": api_key,
        }
        url = "https://www.googleapis.com/youtube/v3/videos?" + urlencode(params)
        response = (self._fetcher or fetch_text)(url)
        try:
            data = json_loads(response.body)
        except ValueError as exc:
            raise ParseError("YouTube metadata response was not valid JSON") from exc
        records = data.get("items") if isinstance(data, dict) else []
        record = records[0] if records else {}
        if not isinstance(record, dict):
            raise ParseError("YouTube metadata response did not contain a video")
        snippet = record.get("snippet") if isinstance(record.get("snippet"), dict) else {}
        details = record.get("contentDetails") if isinstance(record.get("contentDetails"), dict) else {}
        stats = record.get("statistics") if isinstance(record.get("statistics"), dict) else {}
        title = html.unescape(str(snippet.get("title") or video_id))
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        lines = [title]
        if snippet.get("description"):
            lines.append(str(snippet.get("description")))
        if snippet.get("channelTitle"):
            lines.append(f"channel: {snippet.get('channelTitle')}")
        item = RetrievedItem(
            title=title,
            url=watch_url,
            text=compact_text("\n".join(lines)),
            metadata={
                "video_id": video_id,
                "channel": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "duration": details.get("duration"),
                "views": stats.get("viewCount"),
            },
        )
        return SourceResult(self.name, watch_url, title, response.headers.get("Content-Type"), [item], [])


def json_loads(text: str):
    import json

    return json.loads(text)
