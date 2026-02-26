from __future__ import annotations

import feedparser

from app.db.models import Source
from app.services.ingestion.base import SourceConnector
from app.services.ingestion.models import NormalizedItem, utc_now
from app.services.ingestion.utils import parse_datetime


class YouTubeConnector(SourceConnector):
    source_type = "youtube"

    def fetch_latest(self, source: Source, limit: int = 25) -> list[dict]:
        feed = feedparser.parse(source.external_ref)
        return [dict(entry) for entry in feed.entries[:limit]]

    def normalize(self, source: Source, raw_item: dict) -> NormalizedItem:
        url = raw_item.get("link", source.url)
        published = parse_datetime(raw_item.get("published") or raw_item.get("updated"))

        return NormalizedItem(
            source_id=source.id,
            source_type=source.source_type,
            source_name=source.name,
            external_id=raw_item.get("yt_videoid", url),
            author=raw_item.get("author"),
            title=raw_item.get("title", "Untitled"),
            body=raw_item.get("summary", ""),
            url=url,
            published_at=published,
            fetched_at=utc_now(),
            category_candidates=source.category_hints,
            raw_payload=raw_item,
        )
