from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class SummaryDraft:
    provider: str
    model: str
    short_summary: str
    long_summary: str
    changes_bullets: list[str]
    why_it_matters: str | None


class SummarizerProvider(ABC):
    provider_name: str

    @abstractmethod
    def summarize(self, headline: str, evidence: list[str]) -> SummaryDraft:
        raise NotImplementedError
