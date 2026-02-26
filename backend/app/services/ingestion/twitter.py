from __future__ import annotations

from app.db.models import Source
from app.services.ingestion.base import SourceConnector
from app.services.ingestion.models import NormalizedItem


class TwitterConnector(SourceConnector):
    source_type = "twitter"

    def fetch_latest(self, source: Source, limit: int = 25) -> list[dict]:
        return []

    def normalize(self, source: Source, raw_item: dict) -> NormalizedItem:
        raise NotImplementedError("Twitter ingestion adapter is intentionally a placeholder for MVP hardening")
