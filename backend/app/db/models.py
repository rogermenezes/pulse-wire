from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_ref: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    polling_interval_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    category_hints: Mapped[list[str]] = mapped_column(JSON, default=list)
    auth_config: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("run"))
    status: Mapped[str] = mapped_column(String(32), default="running", nullable=False)
    source_filter: Mapped[list[str]] = mapped_column(JSON, default=list)
    fetched_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    normalized_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clustered_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RawIngestedItem(Base):
    __tablename__ = "raw_ingested_items"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_raw_source_external"),
        Index("ix_raw_source_fetched", "source_id", "fetched_at"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("raw"))
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SourceItem(Base):
    __tablename__ = "source_items"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_source_item_external"),
        Index("ix_source_items_published", "published_at"),
        Index("ix_source_items_hash", "content_hash"),
        Index("ix_source_items_dedupe", "dedupe_key"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("item"))
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    raw_item_id: Mapped[str | None] = mapped_column(ForeignKey("raw_ingested_items.id", ondelete="SET NULL"), nullable=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, default="", nullable=False)
    canonical_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    engagement_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    media_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    raw_payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    dedupe_key: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("cat"))
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)


class StoryCluster(Base):
    __tablename__ = "story_clusters"
    __table_args__ = (
        Index("ix_story_clusters_cat_updated", "primary_category_id", "last_updated_at"),
        Index("ix_story_clusters_status_rank", "status", "ranking_score"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("story"))
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    short_headline: Mapped[str | None] = mapped_column(String(240), nullable=True)
    primary_category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="developing", nullable=False)
    representative_item_id: Mapped[str | None] = mapped_column(ForeignKey("source_items.id", ondelete="SET NULL"), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    source_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ranking_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    items: Mapped[list[ClusterItem]] = relationship(back_populates="cluster", cascade="all, delete-orphan")


class ClusterItem(Base):
    __tablename__ = "cluster_items"
    __table_args__ = (
        UniqueConstraint("cluster_id", "source_item_id", name="uq_cluster_source_item"),
        Index("ix_cluster_items_cluster", "cluster_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("ci"))
    cluster_id: Mapped[str] = mapped_column(ForeignKey("story_clusters.id", ondelete="CASCADE"), nullable=False)
    source_item_id: Mapped[str] = mapped_column(ForeignKey("source_items.id", ondelete="CASCADE"), nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cluster: Mapped[StoryCluster] = relationship(back_populates="items")


class Summary(Base):
    __tablename__ = "summaries"
    __table_args__ = (Index("ix_summaries_cluster_generated", "cluster_id", "generated_at"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("sum"))
    cluster_id: Mapped[str] = mapped_column(ForeignKey("story_clusters.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    short_summary: Mapped[str] = mapped_column(Text, nullable=False)
    long_summary: Mapped[str] = mapped_column(Text, nullable=False)
    changes_bullets: Mapped[list[str]] = mapped_column(JSON, default=list)
    why_it_matters: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    summary_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class StoryTag(Base):
    __tablename__ = "story_tags"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("tag"))
    cluster_id: Mapped[str] = mapped_column(ForeignKey("story_clusters.id", ondelete="CASCADE"), nullable=False)
    tag: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
