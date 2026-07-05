from __future__ import annotations

from reachkit.runtime.http import HttpResponse
from reachkit.sources.youtube import YouTubeTranscriptReader, parse_video_id


def test_parse_video_id_accepts_common_youtube_urls():
    assert parse_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert parse_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert parse_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_youtube_transcript_reader_returns_text_records():
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append(url)
        if "type=list" in url:
            return HttpResponse(
                url=url,
                status=200,
                headers={"Content-Type": "text/xml"},
                body='<transcript_list><track id="0" lang_code="en" name="English"/></transcript_list>',
            )
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "text/xml"},
            body='<transcript><text start="0" dur="1.2">Hello</text><text start="1.2" dur="1.1">world</text></transcript>',
        )

    result = YouTubeTranscriptReader(fetcher=fake_fetch).read("https://youtu.be/dQw4w9WgXcQ", lang="en")

    assert result.source == "youtube"
    assert result.items[0].text == "Hello world"
    assert result.items[0].metadata["video_id"] == "dQw4w9WgXcQ"
    assert result.items[0].metadata["language"] == "en"
    assert "lang=en" in calls[1]
