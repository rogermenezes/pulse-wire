from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Base, Category, Source
from app.db.session import engine
from app.services.store import CATEGORIES, load_curated_sources


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_categories(db: Session) -> None:
    for category in CATEGORIES:
        exists = db.scalar(select(Category).where(Category.slug == category["slug"]))
        if exists:
            continue
        db.add(Category(slug=category["slug"], name=category["name"]))
    db.commit()


def seed_sources(db: Session) -> None:
    for source in load_curated_sources():
        existing = db.scalar(select(Source).where(Source.id == source["id"]))
        if existing:
            existing.source_type = source["source_type"]
            existing.name = source["display_name"]
            existing.external_ref = source["handle_or_identifier"]
            existing.url = source.get("url", source["handle_or_identifier"])
            existing.enabled = source["enabled"]
            existing.polling_interval_seconds = source.get("poll_interval_seconds", 300)
            existing.category_hints = source.get("category_hints", [])
            continue

        db.add(
            Source(
                id=source["id"],
                source_type=source["source_type"],
                name=source["display_name"],
                external_ref=source["handle_or_identifier"],
                url=source.get("url", source["handle_or_identifier"]),
                enabled=source["enabled"],
                polling_interval_seconds=source.get("poll_interval_seconds", 300),
                category_hints=source.get("category_hints", []),
                auth_config=source.get("auth_reference", {}),
            )
        )
    db.commit()
