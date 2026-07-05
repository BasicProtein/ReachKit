from __future__ import annotations

import json

import pytest

from reachkit.core.errors import ParseError
from reachkit.runtime.http import HttpResponse
from reachkit.sources.bilibili import BilibiliVideoReader, parse_bvid


def test_parse_bvid_accepts_urls_and_ids():
    assert parse_bvid("BV1xx411c7mD") == "BV1xx411c7mD"
    assert parse_bvid("https://www.bilibili.com/video/BV1xx411c7mD/") == "BV1xx411c7mD"


def test_bilibili_video_reader_accepts_aid_values():
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append(url)
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(
                {
                    "code": 0,
                    "data": {
                        "bvid": "BV1xx411c7mD",
                        "aid": 123,
                        "title": "Demo video",
                        "desc": "",
                        "duration": 120,
                    },
                }
            ),
        )

    result = BilibiliVideoReader(fetcher=fake_fetch).read("av123")

    assert result.items[0].metadata["aid"] == 123
    assert "aid=123" in calls[0]
    assert "bvid=" not in calls[0]


def test_bilibili_video_reader_maps_video_payload():
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append((url, kwargs))
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(
                {
                    "code": 0,
                    "data": {
                        "bvid": "BV1xx411c7mD",
                        "aid": 7,
                        "title": "Demo video",
                        "desc": "A useful public video",
                        "duration": 120,
                        "owner": {"mid": 99, "name": "creator"},
                        "stat": {"view": 1000, "like": 80, "reply": 12},
                    },
                }
            ),
        )

    result = BilibiliVideoReader(fetcher=fake_fetch).read("BV1xx411c7mD")

    assert result.source == "bilibili"
    assert result.items[0].title == "Demo video"
    assert "A useful public video" in result.items[0].text
    assert result.items[0].metadata["bvid"] == "BV1xx411c7mD"
    assert "bvid=BV1xx411c7mD" in calls[0][0]


def test_bilibili_video_reader_rejects_non_object_payload():
    def fake_fetch(url, **kwargs):
        return HttpResponse(
            url=url,
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(["not", "an", "object"]),
        )

    with pytest.raises(ParseError):
        BilibiliVideoReader(fetcher=fake_fetch).read("BV1xx411c7mD")
