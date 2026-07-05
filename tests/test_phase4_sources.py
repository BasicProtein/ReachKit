from __future__ import annotations

import json

from reachkit.runtime.http import HttpResponse
from reachkit.sources.bilibili import BilibiliVideoReader
from reachkit.sources.github import GitHubReader
from reachkit.sources.podcast import PodcastReader
from reachkit.sources.v2ex import V2EXReader
from reachkit.sources.youtube import YouTubeSearchReader


def _json_response(url: str, payload) -> HttpResponse:
    return HttpResponse(url=url, status=200, headers={"Content-Type": "application/json"}, body=json.dumps(payload))


def test_github_reader_reads_issue_pr_and_release():
    calls: list[str] = []

    def fake_fetch(url, **kwargs):
        calls.append(url)
        if "/issues/7" in url:
            return _json_response(
                url,
                {
                    "number": 7,
                    "title": "Issue title",
                    "body": "Issue body",
                    "html_url": "https://github.com/reachkit/demo/issues/7",
                    "state": "open",
                    "user": {"login": "alice"},
                },
            )
        if "/pulls/3" in url:
            return _json_response(
                url,
                {
                    "number": 3,
                    "title": "PR title",
                    "body": "PR body",
                    "html_url": "https://github.com/reachkit/demo/pull/3",
                    "state": "open",
                    "user": {"login": "bob"},
                    "base": {"ref": "main"},
                    "head": {"ref": "feature"},
                },
            )
        return _json_response(
            url,
            {
                "tag_name": "v1.0.0",
                "name": "Version 1",
                "body": "Release notes",
                "html_url": "https://github.com/reachkit/demo/releases/tag/v1.0.0",
                "draft": False,
                "prerelease": False,
            },
        )

    reader = GitHubReader(fetcher=fake_fetch)

    issue = reader.read_issue("reachkit/demo", 7)
    pull = reader.read_pull_request("reachkit/demo", 3)
    release = reader.read_release("reachkit/demo", tag="v1.0.0")

    assert issue.items[0].title == "Issue title"
    assert issue.items[0].metadata["number"] == 7
    assert pull.items[0].metadata["base"] == "main"
    assert release.items[0].metadata["tag_name"] == "v1.0.0"
    assert any("/issues/7" in call for call in calls)
    assert any("/pulls/3" in call for call in calls)
    assert any("/releases/tags/v1.0.0" in call for call in calls)


def test_youtube_search_reader_uses_api_key_without_exposing_it():
    calls = []

    def fake_fetch(url, **kwargs):
        calls.append(url)
        return _json_response(
            url,
            {
                "items": [
                    {
                        "id": {"videoId": "abc123"},
                        "snippet": {
                            "title": "Demo video",
                            "description": "Video description",
                            "channelTitle": "ReachKit channel",
                            "publishedAt": "2026-01-01T00:00:00Z",
                        },
                    }
                ]
            },
        )

    result = YouTubeSearchReader(fetcher=fake_fetch, api_key="secret-key").search("agent tools", limit=1)

    assert result.items[0].title == "Demo video"
    assert result.items[0].metadata["video_id"] == "abc123"
    assert "secret-key" not in result.items[0].text
    assert "key=secret-key" in calls[0]


def test_bilibili_search_returns_video_results():
    def fake_fetch(url, **kwargs):
        return _json_response(
            url,
            {
                "code": 0,
                "data": {
                    "result": [
                        {
                            "title": "<em class=\"keyword\">Demo</em> video",
                            "bvid": "BV1abc",
                            "arcurl": "https://www.bilibili.com/video/BV1abc",
                            "description": "Search text",
                            "author": "creator",
                            "play": 12,
                        }
                    ]
                },
            },
        )

    result = BilibiliVideoReader(fetcher=fake_fetch).search("demo", limit=1)

    assert result.items[0].title == "Demo video"
    assert result.items[0].url == "https://www.bilibili.com/video/BV1abc"
    assert result.items[0].metadata["bvid"] == "BV1abc"


def test_v2ex_reader_reads_hot_topic_and_user():
    def fake_fetch(url, **kwargs):
        if "topics/hot" in url:
            return _json_response(
                url,
                [
                    {
                        "id": 101,
                        "title": "Hot topic",
                        "url": "https://www.v2ex.com/t/101",
                        "content": "Topic body",
                        "node": {"name": "python"},
                        "member": {"username": "alice"},
                    }
                ],
            )
        return _json_response(
            url,
            {
                "username": "alice",
                "url": "https://www.v2ex.com/member/alice",
                "tagline": "Builder",
                "bio": "Writes code",
            },
        )

    reader = V2EXReader(fetcher=fake_fetch)

    hot = reader.hot(limit=1)
    user = reader.user("alice")

    assert hot.items[0].title == "Hot topic"
    assert hot.items[0].metadata["node"] == "python"
    assert user.items[0].title == "alice"
    assert "Writes code" in user.items[0].text


def test_podcast_reader_parses_feed_metadata_and_episodes():
    feed = """<?xml version="1.0"?>
    <rss version="2.0">
      <channel>
        <title>ReachKit Radio</title>
        <description>Agent internet notes</description>
        <link>https://example.com/podcast</link>
        <item>
          <title>Episode one</title>
          <description>Episode notes</description>
          <link>https://example.com/ep1</link>
          <enclosure url="https://example.com/ep1.mp3" type="audio/mpeg" />
        </item>
      </channel>
    </rss>"""

    def fake_fetch(url, **kwargs):
        return HttpResponse(url=url, status=200, headers={"Content-Type": "application/rss+xml"}, body=feed)

    result = PodcastReader(fetcher=fake_fetch).read("https://example.com/feed.xml", limit=2)

    assert result.title == "ReachKit Radio"
    assert result.items[0].title == "Episode one"
    assert result.items[0].metadata["audio_url"] == "https://example.com/ep1.mp3"
