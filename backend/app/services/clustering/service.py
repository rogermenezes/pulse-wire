from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import ClusterItem, SourceItem, StoryCluster
from app.services.clustering.clusterer import cluster_similarity


def _slugify(title: str) -> str:
    base = "-".join(title.lower().split())[:60] or "story"
    return f"{base}-{uuid4().hex[:8]}"


def _ranking_score(cluster: StoryCluster) -> float:
    age_hours = max((datetime.now(timezone.utc) - cluster.last_updated_at).total_seconds() / 3600, 1)
    return (cluster.item_count * 1.7 + cluster.source_count * 2.2) / age_hours


def assign_item_to_cluster(db: Session, item: SourceItem) -> StoryCluster:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.cluster_window_hours)

    candidate_clusters = db.scalars(
        select(StoryCluster).where(StoryCluster.last_updated_at >= cutoff).order_by(desc(StoryCluster.last_updated_at)).limit(100)
    ).all()

    item_text = f"{item.title} {item.body}"
    chosen: StoryCluster | None = None
    chosen_score = 0.0

    for cluster in candidate_clusters:
        cluster_text = cluster.headline
        score = cluster_similarity(item_text, cluster_text, item.published_at, cluster.last_updated_at)
        if score > chosen_score and score >= settings.cluster_similarity_threshold:
            chosen = cluster
            chosen_score = score

    if chosen is None:
        chosen = StoryCluster(
            slug=_slugify(item.title),
            headline=item.title,
            short_headline=item.title[:120],
            status="breaking",
            representative_item_id=item.id,
            first_seen_at=item.published_at,
            last_updated_at=item.published_at,
            item_count=0,
            source_count=0,
            ranking_score=0.0,
        )
        db.add(chosen)
        db.flush()

    existing_link = db.scalar(
        select(ClusterItem).where(ClusterItem.cluster_id == chosen.id, ClusterItem.source_item_id == item.id)
    )

    if not existing_link:
        db.add(
            ClusterItem(
                cluster_id=chosen.id,
                source_item_id=item.id,
                relevance_score=chosen_score or 1.0,
                is_primary=chosen.representative_item_id == item.id,
            )
        )
        db.flush()

    cluster_items = db.scalars(select(ClusterItem).where(ClusterItem.cluster_id == chosen.id)).all()
    source_item_ids = [link.source_item_id for link in cluster_items]

    related_items = db.scalars(select(SourceItem).where(SourceItem.id.in_(source_item_ids))).all() if source_item_ids else []
    sources = {row.source_id for row in related_items}

    chosen.item_count = len(cluster_items)
    chosen.source_count = len(sources)
    chosen.last_updated_at = max([item.published_at] + [row.published_at for row in related_items])
    chosen.status = "breaking" if chosen.item_count <= 3 else "developing"
    chosen.ranking_score = _ranking_score(chosen)

    return chosen
