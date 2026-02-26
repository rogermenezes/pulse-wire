from datetime import timezone

from app.services.ingestion.utils import parse_datetime


def test_parse_datetime_handles_unix_epoch_strings() -> None:
    parsed = parse_datetime("1767000000")
    assert parsed.tzinfo == timezone.utc
    assert parsed.year >= 2025


def test_parse_datetime_handles_iso8601() -> None:
    parsed = parse_datetime("2026-02-26T10:15:00Z")
    assert parsed.tzinfo == timezone.utc
    assert parsed.month == 2
