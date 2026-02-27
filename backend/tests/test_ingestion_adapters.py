from __future__ import annotations

from datetime import timezone

import pytest

from app.db.models import Source
from app.services.ingestion.discord import DiscordConnector
from app.services.ingestion.reddit import RedditConnector
from app.services.ingestion.rss import RSSConnector
from app.services.ingestion.twitter import TwitterConnector
from app.services.ingestion.youtube import YouTubeConnector


def make_source(source_type: str, external_ref: str) -> Source:
    return Source(
        id=f"src_{source_type}_adapter",
        source_type=source_type,
        name=f"{source_type} source",
        external_ref=external_ref,
        url=external_ref,
        enabled=True,
        polling_interval_seconds=300,
        category_hints=["world"],
        auth_config={},
    )


def test_rss_fetch_latest_uses_feedparser(monkeypatch) -> None:
    connector = RSSConnector()
    source = make_source("rss", "https://example.com/rss.xml")

    class DummyFeed:
        entries = [{"id": "1", "title": "a"}, {"id": "2", "title": "b"}]

    monkeypatch.setattr("app.services.ingestion.rss.feedparser.parse", lambda _: DummyFeed())

    items = connector.fetch_latest(source, limit=1)

    assert len(items) == 1
    assert items[0]["id"] == "1"


def test_reddit_fetch_latest_parses_children(monkeypatch) -> None:
    connector = RedditConnector()
    source = make_source("reddit", "worldnews")

    class DummyResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "data": {
                    "children": [
                        {"data": {"id": "a1", "title": "first"}},
                        {"data": {"id": "a2", "title": "second"}},
                    ]
                }
            }

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def get(self, url, params=None):
            assert "/r/worldnews/new.json" in url
            assert params and params["limit"] == 2
            return DummyResponse()

    monkeypatch.setattr("app.services.ingestion.reddit.httpx.Client", DummyClient)

    items = connector.fetch_latest(source, limit=2)

    assert [item["id"] for item in items] == ["a1", "a2"]


def test_youtube_normalization_parses_video_fields() -> None:
    connector = YouTubeConnector()
    source = make_source("youtube", "https://www.youtube.com/feeds/videos.xml?channel_id=test")
    raw = {
        "yt_videoid": "vid123",
        "title": "New video",
        "summary": "Video summary",
        "link": "https://youtube.com/watch?v=vid123",
        "author": "Channel",
        "published": "2026-02-26T10:15:00Z",
    }

    normalized = connector.normalize(source, raw)

    assert normalized.external_id == "vid123"
    assert normalized.title == "New video"
    assert normalized.url.endswith("vid123")
    assert normalized.published_at.tzinfo == timezone.utc


def test_placeholder_adapters_are_stubbed() -> None:
    source_x = make_source("twitter", "IndianExpress")
    source_discord = make_source("discord", "server:example")

    twitter = TwitterConnector()
    discord = DiscordConnector()

    assert twitter.fetch_latest(source_x) == []
    assert discord.fetch_latest(source_discord) == []

    with pytest.raises(NotImplementedError):
        twitter.normalize(source_x, {})

    with pytest.raises(NotImplementedError):
        discord.normalize(source_discord, {})
