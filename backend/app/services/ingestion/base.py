from __future__ import annotations

from abc import ABC, abstractmethod

from app.db.models import Source
from app.services.ingestion.models import NormalizedItem


class SourceConnector(ABC):
    source_type: str

    @abstractmethod
    def fetch_latest(self, source: Source, limit: int = 25) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def normalize(self, source: Source, raw_item: dict) -> NormalizedItem:
        raise NotImplementedError

    def validate(self, raw_item: dict) -> bool:
        return bool(raw_item)
