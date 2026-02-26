from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import IngestionRun, RawIngestedItem, Source, SourceItem, StoryCluster
from app.services.clustering.service import assign_item_to_cluster
from app.services.ingestion.models import NormalizedItem
from app.services.ingestion.registry import get_connector
from app.services.summarization.service import summarize_cluster


@dataclass(slots=True)
class PipelineResult:
    fetched_count: int
    normalized_count: int
    clustered_count: int


def _upsert_source_item(db: Session, normalized: NormalizedItem, raw_item_id: str | None) -> tuple[SourceItem, bool]:
    existing = db.scalar(
        select(SourceItem).where(SourceItem.source_id == normalized.source_id, SourceItem.external_id == normalized.external_id)
    )

    if existing:
        existing.author = normalized.author
        existing.title = normalized.title
        existing.body = normalized.body
        existing.canonical_url = normalized.url
        existing.published_at = normalized.published_at
        existing.fetched_at = normalized.fetched_at
        existing.language = normalized.language
        existing.engagement_json = normalized.engagement
        existing.media_json = normalized.media
        existing.raw_payload_json = normalized.raw_payload
        existing.content_hash = normalized.content_hash
        existing.dedupe_key = normalized.dedupe_key
        existing.raw_item_id = raw_item_id
        return existing, False

    created = SourceItem(
        source_id=normalized.source_id,
        raw_item_id=raw_item_id,
        external_id=normalized.external_id,
        author=normalized.author,
        title=normalized.title,
        body=normalized.body,
        canonical_url=normalized.url,
        published_at=normalized.published_at,
        fetched_at=normalized.fetched_at,
        language=normalized.language,
        engagement_json=normalized.engagement,
        media_json=normalized.media,
        raw_payload_json=normalized.raw_payload,
        content_hash=normalized.content_hash,
        dedupe_key=normalized.dedupe_key,
    )
    db.add(created)
    db.flush()
    return created, True


def run_ingestion_pipeline(db: Session, source_types: list[str] | None = None) -> PipelineResult:
    run = IngestionRun(source_filter=source_types or [])
    db.add(run)
    db.flush()

    source_query = select(Source).where(Source.enabled.is_(True))
    if source_types:
        source_query = source_query.where(Source.source_type.in_(source_types))

    sources = db.scalars(source_query).all()

    fetched_count = 0
    normalized_count = 0
    clustered_count = 0
    touched_cluster_ids: set[str] = set()

    for source in sources:
        connector = get_connector(source.source_type)
        if connector is None:
            continue

        try:
            raw_items = connector.fetch_latest(source, limit=settings.ingestion_default_limit)
        except Exception:
            continue
        fetched_count += len(raw_items)

        for raw in raw_items:
            if not connector.validate(raw):
                continue

            try:
                normalized = connector.normalize(source, raw)
            except Exception:
                continue

            external_id = normalized.external_id
            raw_existing = db.scalar(
                select(RawIngestedItem).where(RawIngestedItem.source_id == source.id, RawIngestedItem.external_id == external_id)
            )
            if raw_existing:
                raw_existing.payload_json = raw
                raw_record = raw_existing
            else:
                raw_record = RawIngestedItem(source_id=source.id, external_id=external_id, payload_json=raw)
                db.add(raw_record)
                db.flush()

            row, created = _upsert_source_item(db, normalized, raw_record.id)
            if created:
                normalized_count += 1
            cluster = assign_item_to_cluster(db, row)
            touched_cluster_ids.add(cluster.id)
            clustered_count += 1

    for cluster_id in touched_cluster_ids:
        cluster = db.get(StoryCluster, cluster_id)
        if cluster is None:
            continue
        summarize_cluster(db, cluster)

    run.fetched_count = fetched_count
    run.normalized_count = normalized_count
    run.clustered_count = clustered_count
    run.status = "completed"
    run.completed_at = datetime.now(timezone.utc)
    db.commit()

    return PipelineResult(
        fetched_count=fetched_count,
        normalized_count=normalized_count,
        clustered_count=clustered_count,
    )
