from __future__ import annotations

import httpx

from app.core.config import settings
from app.db.models import Source
from app.services.ingestion.base import SourceConnector
from app.services.ingestion.models import NormalizedItem, utc_now
from app.services.ingestion.utils import parse_datetime


class RedditConnector(SourceConnector):
    source_type = "reddit"

    def fetch_latest(self, source: Source, limit: int = 25) -> list[dict]:
        subreddit = source.external_ref.strip().replace("r/", "")
        url = f"https://www.reddit.com/r/{subreddit}/new.json"
        headers = {"User-Agent": settings.reddit_user_agent}
        params = {"limit": min(limit, 100), "raw_json": 1}
        with httpx.Client(timeout=settings.ingestion_timeout_seconds, headers=headers) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        posts: list[dict] = []
        for child in data.get("data", {}).get("children", []):
            posts.append(child.get("data", {}))
        return posts

    def normalize(self, source: Source, raw_item: dict) -> NormalizedItem:
        permalink = raw_item.get("permalink", "")
        url = raw_item.get("url_overridden_by_dest") or f"https://reddit.com{permalink}"
        body = raw_item.get("selftext") or ""
        published = parse_datetime(raw_item.get("created_utc"))

        return NormalizedItem(
            source_id=source.id,
            source_type=source.source_type,
            source_name=source.name,
            external_id=raw_item.get("id", url),
            author=raw_item.get("author"),
            title=raw_item.get("title", "Untitled"),
            body=body,
            url=url,
            published_at=published,
            fetched_at=utc_now(),
            engagement={
                "upvotes": raw_item.get("ups", 0),
                "comments": raw_item.get("num_comments", 0),
            },
            category_candidates=source.category_hints,
            raw_payload=raw_item,
        )
