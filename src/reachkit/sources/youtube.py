from __future__ import annotations

from collections.abc import Callable
import html
from urllib.parse import parse_qs, urlencode, urlparse
import xml.etree.ElementTree as ET

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
