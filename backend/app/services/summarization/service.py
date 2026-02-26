from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import ClusterItem, SourceItem, StoryCluster, Summary
from app.services.summarization.anthropic_provider import AnthropicProvider
from app.services.summarization.base import SummaryDraft, SummarizerProvider
from app.services.summarization.openai_provider import OpenAIProvider


class StubProvider(SummarizerProvider):
    provider_name = "stub"

    def summarize(self, headline: str, evidence: list[str]) -> SummaryDraft:
        return SummaryDraft(
            provider=self.provider_name,
            model="deterministic-v1",
            short_summary=f"{headline}: {len(evidence)} curated updates in this cluster.",
            long_summary=" ".join(evidence[:4]) if evidence else headline,
            changes_bullets=evidence[:3],
            why_it_matters="Signals from multiple manually curated sources indicate this story is evolving.",
        )


def get_provider() -> SummarizerProvider:
    if settings.summarization_provider == "openai":
        return OpenAIProvider()
    if settings.summarization_provider == "anthropic":
        return AnthropicProvider()
    return StubProvider()


def summarize_cluster(db: Session, cluster: StoryCluster) -> Summary:
    links = db.scalars(select(ClusterItem).where(ClusterItem.cluster_id == cluster.id)).all()
    source_item_ids = [link.source_item_id for link in links]
    items = db.scalars(select(SourceItem).where(SourceItem.id.in_(source_item_ids))).all() if source_item_ids else []

    evidence = [f"{item.title} ({item.canonical_url})" for item in sorted(items, key=lambda row: row.published_at, reverse=True)]
    provider = get_provider()
    draft = provider.summarize(cluster.headline, evidence)

    latest_summary = db.scalar(
        select(Summary)
        .where(Summary.cluster_id == cluster.id, Summary.invalidated_at.is_(None))
        .order_by(Summary.generated_at.desc())
    )

    if latest_summary:
        latest_summary.invalidated_at = cluster.last_updated_at

    summary = Summary(
        cluster_id=cluster.id,
        provider=draft.provider,
        model=draft.model,
        short_summary=draft.short_summary,
        long_summary=draft.long_summary,
        changes_bullets=draft.changes_bullets,
        why_it_matters=draft.why_it_matters,
        source_snapshot_json={"item_ids": source_item_ids},
        summary_version=(latest_summary.summary_version + 1) if latest_summary else 1,
    )
    db.add(summary)
    db.flush()
    return summary
