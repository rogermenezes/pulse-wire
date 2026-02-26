from datetime import timezone

from app.db.models import Source
from app.services.ingestion.reddit import RedditConnector
from app.services.ingestion.rss import RSSConnector


def make_source(source_type: str, external_ref: str) -> Source:
    return Source(
        id=f"src_{source_type}_test",
        source_type=source_type,
        name=f"{source_type} source",
        external_ref=external_ref,
        url=external_ref,
        enabled=True,
        polling_interval_seconds=300,
        category_hints=["world"],
        auth_config={},
    )


def test_rss_normalization_parses_core_fields() -> None:
    connector = RSSConnector()
    source = make_source("rss", "https://example.com/feed.xml")
    raw = {
        "id": "entry-123",
        "title": "Breaking: Something happened",
        "summary": "Story body",
        "link": "https://example.com/story",
        "published": "Wed, 25 Feb 2026 12:00:00 GMT",
        "author": "Reporter",
    }

    normalized = connector.normalize(source, raw)

    assert normalized.external_id == "entry-123"
    assert normalized.title == "Breaking: Something happened"
    assert normalized.url == "https://example.com/story"
    assert normalized.author == "Reporter"
    assert normalized.published_at.tzinfo == timezone.utc
    assert normalized.category_candidates == ["world"]


def test_reddit_normalization_includes_engagement() -> None:
    connector = RedditConnector()
    source = make_source("reddit", "worldnews")
    raw = {
        "id": "abc123",
        "title": "Reddit headline",
        "selftext": "Post body",
        "permalink": "/r/worldnews/comments/abc123/sample/",
        "created_utc": 1767000000,
        "author": "news_mod",
        "ups": 321,
        "num_comments": 45,
    }

    normalized = connector.normalize(source, raw)

    assert normalized.external_id == "abc123"
    assert normalized.url.startswith("https://reddit.com/r/worldnews")
    assert normalized.engagement["upvotes"] == 321
    assert normalized.engagement["comments"] == 45
    assert normalized.published_at.tzinfo == timezone.utc
