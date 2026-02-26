from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


def parse_datetime(value: str | int | float | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)

    stripped = value.strip()
    if stripped.isdigit():
        return datetime.fromtimestamp(int(stripped), tz=timezone.utc)

    try:
        dt = parsedate_to_datetime(stripped)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError):
        pass

    try:
        normalized = stripped.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)
