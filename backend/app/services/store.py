import json
from datetime import datetime, timezone
from pathlib import Path

from app.schemas import StoryDetail

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CATEGORIES = [
    {"slug": "breaking", "name": "Breaking News"},
    {"slug": "world", "name": "World"},
    {"slug": "sports", "name": "Sports"},
    {"slug": "ai-tech", "name": "AI and Tech"},
    {"slug": "finance", "name": "Finance"},
]


def load_curated_sources() -> list[dict]:
    sources_path = DATA_DIR / "sources.seed.json"
    with sources_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def seeded_stories() -> list[StoryDetail]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return [
        StoryDetail(
            id="story_001",
            headline="Major cloud outage reports trigger cross-platform alerts",
            short_summary="Manually curated RSS and Reddit sources report widespread cloud disruptions.",
            long_summary=(
                "PulseWire grouped multiple manually curated sources discussing a major cloud outage. "
                "The cluster is marked breaking while ingestion and summarization pipelines are scaffolded."
            ),
            primary_category="Breaking News",
            status="breaking",
            source_count=3,
            last_updated_at=now,
            sources=[
                {
                    "source_name": "Reuters RSS",
                    "source_type": "rss",
                    "url": "https://www.reuters.com/world/",
                    "published_at": now,
                },
                {
                    "source_name": "r/worldnews",
                    "source_type": "reddit",
                    "url": "https://www.reddit.com/r/worldnews/",
                    "published_at": now,
                },
                {
                    "source_name": "@example_handle",
                    "source_type": "twitter",
                    "url": "https://x.com/example_handle",
                    "published_at": now,
                },
            ],
        )
    ]
