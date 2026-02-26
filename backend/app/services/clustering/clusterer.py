from __future__ import annotations

import re
from datetime import datetime, timezone
from math import exp

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]{3,}")


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(text)}


def jaccard_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    intersection = len(left & right)
    union = len(left | right)
    if union == 0:
        return 0.0
    return intersection / union


def recency_weight(published_at: datetime, reference: datetime) -> float:
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    hours = abs((reference - published_at).total_seconds()) / 3600
    return exp(-hours / 72)


def cluster_similarity(item_text: str, cluster_text: str, item_time: datetime, cluster_time: datetime) -> float:
    lexical = jaccard_similarity(tokenize(item_text), tokenize(cluster_text))
    time_boost = recency_weight(item_time, cluster_time)
    return (0.75 * lexical) + (0.25 * time_boost)
