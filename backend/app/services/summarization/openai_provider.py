from __future__ import annotations

from openai import OpenAI

from app.core.config import settings
from app.services.summarization.base import SummaryDraft, SummarizerProvider


class OpenAIProvider(SummarizerProvider):
    provider_name = "openai"

    def summarize(self, headline: str, evidence: list[str]) -> SummaryDraft:
        if not settings.openai_api_key:
            return SummaryDraft(
                provider=self.provider_name,
                model=settings.openai_model,
                short_summary=f"{headline}: summarized from {len(evidence)} curated source item(s).",
                long_summary="OpenAI API key not configured; generated deterministic fallback summary.",
                changes_bullets=evidence[:3],
                why_it_matters="Multiple curated sources are converging on this story.",
            )

        client = OpenAI(api_key=settings.openai_api_key)
        joined_evidence = "\n".join(f"- {item}" for item in evidence[:8])
        prompt = (
            "Summarize this story cluster with a short and long summary, with factual grounding only.\n"
            f"Headline: {headline}\nEvidence:\n{joined_evidence}"
        )
        response = client.responses.create(model=settings.openai_model, input=prompt)
        text = response.output_text or headline

        return SummaryDraft(
            provider=self.provider_name,
            model=settings.openai_model,
            short_summary=text.split("\n")[0][:220],
            long_summary=text,
            changes_bullets=evidence[:3],
            why_it_matters="This cluster includes corroboration from manually curated feeds.",
        )
