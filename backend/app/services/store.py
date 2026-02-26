import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Category, ClusterItem, Source, SourceItem, StoryCluster, Summary
from app.schemas import StoryCard, StoryDetail

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CATEGORIES = [
    {"slug": "breaking", "name": "Breaking News"},
    {"slug": "world", "name": "World"},
    {"slug": "us", "name": "US"},
    {"slug": "politics", "name": "Politics"},
    {"slug": "sports", "name": "Sports"},
    {"slug": "ai-tech", "name": "AI and Tech"},
    {"slug": "finance", "name": "Finance"},
    {"slug": "business", "name": "Business"},
    {"slug": "science", "name": "Science"},
    {"slug": "entertainment", "name": "Entertainment"},
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
            long_summary="First scaffold fallback story when no clusters exist in Postgres yet.",
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
                    "source_name": "Example YouTube Channel",
                    "source_type": "youtube",
                    "url": "https://www.youtube.com/@example",
                    "published_at": now,
                },
            ],
        )
    ]


def get_categories(db: Session) -> list[dict]:
    rows = db.scalars(select(Category).order_by(Category.name.asc())).all()
    if not rows:
        return CATEGORIES
    return [{"slug": row.slug, "name": row.name} for row in rows]


def _category_name(db: Session, category_id: str | None) -> str:
    if not category_id:
        return "Breaking News"
    category = db.get(Category, category_id)
    return category.name if category else "Breaking News"


def _latest_summary(db: Session, cluster_id: str) -> Summary | None:
    return db.scalar(
        select(Summary)
        .where(Summary.cluster_id == cluster_id, Summary.invalidated_at.is_(None))
        .order_by(Summary.generated_at.desc())
    )


def get_story_cards(db: Session, limit: int, status: str | None = None, category_slug: str | None = None) -> list[StoryCard]:
    query = select(StoryCluster).order_by(StoryCluster.ranking_score.desc(), StoryCluster.last_updated_at.desc()).limit(limit)

    if status:
        query = query.where(StoryCluster.status == status)

    if category_slug:
        category = db.scalar(select(Category).where(Category.slug == category_slug))
        if category:
            query = query.where(StoryCluster.primary_category_id == category.id)
        else:
            return []

    clusters = db.scalars(query).all()
    cards: list[StoryCard] = []

    for cluster in clusters:
        summary = _latest_summary(db, cluster.id)
        cards.append(
            StoryCard(
                id=cluster.id,
                headline=cluster.headline,
                short_summary=summary.short_summary if summary else "Summary pending.",
                primary_category=_category_name(db, cluster.primary_category_id),
                status=cluster.status,
                source_count=cluster.source_count,
                last_updated_at=cluster.last_updated_at,
            )
        )

    return cards


def get_story_detail(db: Session, story_id: str) -> StoryDetail | None:
    cluster = db.get(StoryCluster, story_id)
    if not cluster:
        return None

    summary = _latest_summary(db, cluster.id)
    links = db.scalars(select(ClusterItem).where(ClusterItem.cluster_id == cluster.id)).all()
    item_ids = [link.source_item_id for link in links]
    items = db.scalars(select(SourceItem).where(SourceItem.id.in_(item_ids))).all() if item_ids else []

    source_by_id = {source.id: source for source in db.scalars(select(Source)).all()}

    sources = [
        {
            "source_name": source_by_id[item.source_id].name if item.source_id in source_by_id else "Unknown",
            "source_type": source_by_id[item.source_id].source_type if item.source_id in source_by_id else "unknown",
            "url": item.canonical_url,
            "published_at": item.published_at,
        }
        for item in sorted(items, key=lambda row: row.published_at, reverse=True)
    ]

    return StoryDetail(
        id=cluster.id,
        headline=cluster.headline,
        short_summary=summary.short_summary if summary else "Summary pending.",
        long_summary=summary.long_summary if summary else "Summary pending.",
        primary_category=_category_name(db, cluster.primary_category_id),
        status=cluster.status,
        source_count=cluster.source_count,
        last_updated_at=cluster.last_updated_at,
        sources=sources,
    )
