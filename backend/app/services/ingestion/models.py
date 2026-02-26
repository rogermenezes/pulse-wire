from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class NormalizedItem:
    source_id: str
    source_type: str
    source_name: str
    external_id: str
    author: str | None
    title: str
    body: str
    url: str
    published_at: datetime
    fetched_at: datetime
    language: str = "en"
    engagement: dict = field(default_factory=dict)
    category_candidates: list[str] = field(default_factory=list)
    media: dict = field(default_factory=dict)
    raw_payload: dict = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        payload = f"{self.title}\n{self.body}\n{self.url}".strip().lower()
        return sha256(payload.encode("utf-8")).hexdigest()

    @property
    def dedupe_key(self) -> str:
        payload = self.url.strip().lower() or f"{self.source_type}:{self.external_id}"
        return sha256(payload.encode("utf-8")).hexdigest()
