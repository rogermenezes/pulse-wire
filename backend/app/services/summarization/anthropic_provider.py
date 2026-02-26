from __future__ import annotations

from anthropic import Anthropic

from app.core.config import settings
from app.services.summarization.base import SummaryDraft, SummarizerProvider


class AnthropicProvider(SummarizerProvider):
    provider_name = "anthropic"

    def summarize(self, headline: str, evidence: list[str]) -> SummaryDraft:
        if not settings.anthropic_api_key:
            return SummaryDraft(
                provider=self.provider_name,
                model=settings.anthropic_model,
                short_summary=f"{headline}: summarized from {len(evidence)} curated source item(s).",
                long_summary="Anthropic API key not configured; generated deterministic fallback summary.",
                changes_bullets=evidence[:3],
                why_it_matters="Story importance is inferred from repeated mentions across curated sources.",
            )

        client = Anthropic(api_key=settings.anthropic_api_key)
        joined_evidence = "\n".join(f"- {item}" for item in evidence[:8])
        message = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=600,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Summarize this story with grounded facts only. Return one short summary and one longer summary.\n"
                        f"Headline: {headline}\nEvidence:\n{joined_evidence}"
                    ),
                }
            ],
        )

        text_parts = [part.text for part in message.content if hasattr(part, "text")]
        text = "\n".join(text_parts).strip() or headline

        return SummaryDraft(
            provider=self.provider_name,
            model=settings.anthropic_model,
            short_summary=text.split("\n")[0][:220],
            long_summary=text,
            changes_bullets=evidence[:3],
            why_it_matters="The update reflects corroboration from independent curated feeds.",
        )
