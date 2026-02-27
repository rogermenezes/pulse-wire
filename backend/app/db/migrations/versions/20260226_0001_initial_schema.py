"""initial schema for ingestion and story processing

Revision ID: 20260226_0001
Revises: 
Create Date: 2026-02-26 12:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260226_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source_filter", sa.JSON(), nullable=False),
        sa.Column("fetched_count", sa.Integer(), nullable=False),
        sa.Column("normalized_count", sa.Integer(), nullable=False),
        sa.Column("clustered_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("external_ref", sa.String(length=500), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("polling_interval_seconds", sa.Integer(), nullable=False),
        sa.Column("category_hints", sa.JSON(), nullable=False),
        sa.Column("auth_config", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sources_source_type", "sources", ["source_type"], unique=False)

    op.create_table(
        "raw_ingested_items",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_raw_source_external"),
    )
    op.create_index("ix_raw_source_fetched", "raw_ingested_items", ["source_id", "fetched_at"], unique=False)

    op.create_table(
        "source_items",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("raw_item_id", sa.String(length=64), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("canonical_url", sa.String(length=1000), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("engagement_json", sa.JSON(), nullable=False),
        sa.Column("media_json", sa.JSON(), nullable=False),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("dedupe_key", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["raw_item_id"], ["raw_ingested_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_source_item_external"),
    )
    op.create_index("ix_source_items_dedupe", "source_items", ["dedupe_key"], unique=False)
    op.create_index("ix_source_items_hash", "source_items", ["content_hash"], unique=False)
    op.create_index("ix_source_items_published", "source_items", ["published_at"], unique=False)

    op.create_table(
        "story_clusters",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("slug", sa.String(length=300), nullable=False),
        sa.Column("headline", sa.String(length=500), nullable=False),
        sa.Column("short_headline", sa.String(length=240), nullable=True),
        sa.Column("primary_category_id", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("representative_item_id", sa.String(length=64), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("ranking_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["primary_category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["representative_item_id"], ["source_items.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_story_clusters_cat_updated", "story_clusters", ["primary_category_id", "last_updated_at"], unique=False)
    op.create_index("ix_story_clusters_status_rank", "story_clusters", ["status", "ranking_score"], unique=False)

    op.create_table(
        "cluster_items",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("cluster_id", sa.String(length=64), nullable=False),
        sa.Column("source_item_id", sa.String(length=64), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["cluster_id"], ["story_clusters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_item_id"], ["source_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cluster_id", "source_item_id", name="uq_cluster_source_item"),
    )
    op.create_index("ix_cluster_items_cluster", "cluster_items", ["cluster_id"], unique=False)

    op.create_table(
        "story_tags",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("cluster_id", sa.String(length=64), nullable=False),
        sa.Column("tag", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["cluster_id"], ["story_clusters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_story_tags_tag", "story_tags", ["tag"], unique=False)

    op.create_table(
        "summaries",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("cluster_id", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("short_summary", sa.Text(), nullable=False),
        sa.Column("long_summary", sa.Text(), nullable=False),
        sa.Column("changes_bullets", sa.JSON(), nullable=False),
        sa.Column("why_it_matters", sa.Text(), nullable=True),
        sa.Column("source_snapshot_json", sa.JSON(), nullable=False),
        sa.Column("summary_version", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["cluster_id"], ["story_clusters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_summaries_cluster_generated", "summaries", ["cluster_id", "generated_at"], unique=False)

    op.bulk_insert(
        sa.table(
            "categories",
            sa.column("id", sa.String()),
            sa.column("slug", sa.String()),
            sa.column("name", sa.String()),
        ),
        [
            {"id": "cat_breaking", "slug": "breaking", "name": "Breaking News"},
            {"id": "cat_world", "slug": "world", "name": "World"},
            {"id": "cat_us", "slug": "us", "name": "US"},
            {"id": "cat_politics", "slug": "politics", "name": "Politics"},
            {"id": "cat_sports", "slug": "sports", "name": "Sports"},
            {"id": "cat_ai_tech", "slug": "ai-tech", "name": "AI and Tech"},
            {"id": "cat_finance", "slug": "finance", "name": "Finance"},
            {"id": "cat_business", "slug": "business", "name": "Business"},
            {"id": "cat_science", "slug": "science", "name": "Science"},
            {"id": "cat_entertainment", "slug": "entertainment", "name": "Entertainment"},
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_summaries_cluster_generated", table_name="summaries")
    op.drop_table("summaries")

    op.drop_index("ix_story_tags_tag", table_name="story_tags")
    op.drop_table("story_tags")

    op.drop_index("ix_cluster_items_cluster", table_name="cluster_items")
    op.drop_table("cluster_items")

    op.drop_index("ix_story_clusters_status_rank", table_name="story_clusters")
    op.drop_index("ix_story_clusters_cat_updated", table_name="story_clusters")
    op.drop_table("story_clusters")

    op.drop_index("ix_source_items_published", table_name="source_items")
    op.drop_index("ix_source_items_hash", table_name="source_items")
    op.drop_index("ix_source_items_dedupe", table_name="source_items")
    op.drop_table("source_items")

    op.drop_index("ix_raw_source_fetched", table_name="raw_ingested_items")
    op.drop_table("raw_ingested_items")

    op.drop_index("ix_sources_source_type", table_name="sources")
    op.drop_table("sources")

    op.drop_table("ingestion_runs")
    op.drop_table("categories")
