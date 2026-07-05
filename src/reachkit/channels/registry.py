from __future__ import annotations

from reachkit.channels.models import ChannelCapability, ChannelDefinition
from reachkit.channels.providers import (
    bilibili,
    browser,
    facebook,
    github,
    instagram,
    linkedin,
    podcast,
    reddit,
    rss,
    v2ex,
    web,
    x_platform,
    xiaohongshu,
    xueqiu,
    youtube,
)
from reachkit.core.errors import InputError


class ChannelRegistry:
    def __init__(self, channels: list[ChannelDefinition] | None = None) -> None:
        self._channels: dict[str, ChannelDefinition] = {}
        for channel in channels or []:
            self.register(channel)

    def register(self, channel: ChannelDefinition) -> None:
        self._channels[channel.name] = channel

    def get(self, name: str) -> ChannelDefinition:
        try:
            return self._channels[name]
        except KeyError as exc:
            raise InputError("Unknown channel") from exc

    def names(self) -> list[str]:
        return list(self._channels)

    def all(self) -> list[ChannelDefinition]:
        return list(self._channels.values())


def _capability(kind, label: str, requires_auth: bool = False) -> ChannelCapability:
    return ChannelCapability(kind=kind, label=label, requires_auth=requires_auth)


def default_channel_registry() -> ChannelRegistry:
    return ChannelRegistry(
        [
            ChannelDefinition(
                name="web",
                label="Web",
                capabilities=[
                    _capability("read", "Read public URLs"),
                    _capability("metadata", "Extract page title"),
                    _capability("search", "Search through a configured JSON endpoint", requires_auth=True),
                ],
                provider_checks=[web.provider_statuses],
            ),
            ChannelDefinition(
                name="rss",
                label="RSS / Atom",
                capabilities=[
                    _capability("read", "Read RSS or Atom feeds"),
                    _capability("metadata", "Read feed entries"),
                ],
                provider_checks=[rss.provider_statuses],
            ),
            ChannelDefinition(
                name="github",
                label="GitHub",
                capabilities=[
                    _capability("read", "Read repositories and files"),
                    _capability("search", "Search public repositories"),
                    _capability("metadata", "Read repository metadata"),
                    _capability("comments", "Read issues, pull requests, and releases"),
                ],
                provider_checks=[github.provider_statuses],
            ),
            ChannelDefinition(
                name="youtube",
                label="YouTube",
                capabilities=[
                    _capability("transcript", "Read public timed text"),
                    _capability("read", "Read transcript records"),
                    _capability("metadata", "Read video metadata", requires_auth=True),
                    _capability("search", "Search videos", requires_auth=True),
                ],
                provider_checks=[youtube.provider_statuses],
            ),
            ChannelDefinition(
                name="x",
                label="X",
                capabilities=[
                    _capability("read", "Read a single post", requires_auth=True),
                    _capability("search", "Search recent posts", requires_auth=True),
                    _capability("timeline", "Read user timeline results", requires_auth=True),
                ],
                provider_checks=[x_platform.provider_statuses],
            ),
            ChannelDefinition(
                name="bilibili",
                label="Bilibili",
                capabilities=[
                    _capability("metadata", "Read public video metadata"),
                    _capability("read", "Read video records"),
                    _capability("search", "Search public videos"),
                ],
                provider_checks=[bilibili.provider_statuses],
            ),
            ChannelDefinition(
                name="xiaohongshu",
                label="Xiaohongshu",
                capabilities=[
                    _capability("read", "Read open API JSON", requires_auth=True),
                    _capability("search", "Search notes through configured open API access", requires_auth=True),
                    _capability("comments", "Read note comments through configured open API access", requires_auth=True),
                ],
                provider_checks=[xiaohongshu.provider_statuses],
            ),
            ChannelDefinition(
                name="browser",
                label="Browser",
                capabilities=[
                    _capability("read", "Read rendered page text"),
                    _capability("metadata", "Read rendered page title"),
                ],
                provider_checks=[browser.provider_statuses],
            ),
            ChannelDefinition(
                name="v2ex",
                label="V2EX",
                capabilities=[
                    _capability("read", "Read public topics and users"),
                    _capability("search", "Read hot and node topic lists"),
                    _capability("comments", "Read topic replies"),
                ],
                provider_checks=[v2ex.provider_statuses],
            ),
            ChannelDefinition(
                name="podcast",
                label="Podcast",
                capabilities=[
                    _capability("read", "Read podcast feeds"),
                    _capability("metadata", "Read episode metadata"),
                    _capability("transcript", "Transcribe audio with optional tooling", requires_auth=False),
                ],
                provider_checks=[podcast.provider_statuses],
            ),
            ChannelDefinition(
                name="reddit",
                label="Reddit",
                capabilities=[
                    _capability("read", "Read public posts and comments"),
                    _capability("search", "Search public posts"),
                    _capability("comments", "Read comment listings"),
                ],
                provider_checks=[reddit.provider_statuses],
            ),
            ChannelDefinition(
                name="linkedin",
                label="LinkedIn",
                capabilities=[
                    _capability("read", "Read public pages"),
                    _capability("metadata", "Read public profile or company page text"),
                ],
                provider_checks=[linkedin.provider_statuses],
            ),
            ChannelDefinition(
                name="xueqiu",
                label="Xueqiu",
                capabilities=[
                    _capability("read", "Read stock quotes"),
                    _capability("search", "Search stocks"),
                    _capability("metadata", "Read hot stock records"),
                ],
                provider_checks=[xueqiu.provider_statuses],
            ),
            ChannelDefinition(
                name="facebook",
                label="Facebook",
                capabilities=[
                    _capability("read", "Read authorized page records", requires_auth=True),
                    _capability("search", "Search authorized page records", requires_auth=True),
                    _capability("timeline", "Read authorized feed records", requires_auth=True),
                ],
                provider_checks=[facebook.provider_statuses],
            ),
            ChannelDefinition(
                name="instagram",
                label="Instagram",
                capabilities=[
                    _capability("read", "Read authorized profile records", requires_auth=True),
                    _capability("search", "Search authorized hashtag records", requires_auth=True),
                    _capability("metadata", "Read authorized media metadata", requires_auth=True),
                ],
                provider_checks=[instagram.provider_statuses],
            ),
        ]
    )
