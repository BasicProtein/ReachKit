from __future__ import annotations


def test_source_readers_are_available_from_package():
    from reachkit.sources import (
        BilibiliVideoReader,
        BrowserReader,
        GitHubReader,
        RssReader,
        WebReader,
        XiaohongshuApiReader,
        XPostReader,
        YouTubeTranscriptReader,
    )

    assert WebReader.__name__ == "WebReader"
    assert RssReader.__name__ == "RssReader"
    assert GitHubReader.__name__ == "GitHubReader"
    assert YouTubeTranscriptReader.__name__ == "YouTubeTranscriptReader"
    assert XPostReader.__name__ == "XPostReader"
    assert XiaohongshuApiReader.__name__ == "XiaohongshuApiReader"
    assert BilibiliVideoReader.__name__ == "BilibiliVideoReader"
    assert BrowserReader.__name__ == "BrowserReader"


def test_cookie_helper_is_available_from_package():
    from reachkit.runtime import load_cookie_header

    assert callable(load_cookie_header)
