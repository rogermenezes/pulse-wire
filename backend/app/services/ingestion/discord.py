from __future__ import annotations

from app.db.models import Source
from app.services.ingestion.base import SourceConnector
from app.services.ingestion.models import NormalizedItem


class DiscordConnector(SourceConnector):
    source_type = "discord"

    def fetch_latest(self, source: Source, limit: int = 25) -> list[dict]:
        return []

    def normalize(self, source: Source, raw_item: dict) -> NormalizedItem:
        raise NotImplementedError("Discord ingestion adapter is intentionally a placeholder for MVP hardening")
