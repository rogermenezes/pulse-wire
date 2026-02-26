from datetime import datetime, timedelta, timezone

from app.services.clustering.clusterer import cluster_similarity, tokenize


def test_tokenize_drops_short_tokens() -> None:
    tokens = tokenize("AI in US market jumps on major earnings")
    assert "ai" not in tokens
    assert "market" in tokens
    assert "earnings" in tokens


def test_cluster_similarity_favors_related_recent_items() -> None:
    now = datetime.now(timezone.utc)
    related = cluster_similarity(
        "Major cloud outage across regions affects storage systems",
        "Cloud outage impacts multiple regions and storage availability",
        now,
        now - timedelta(hours=2),
    )
    unrelated = cluster_similarity(
        "Local sports team signs new player",
        "Cloud outage impacts multiple regions and storage availability",
        now,
        now - timedelta(hours=2),
    )

    assert related > unrelated
    assert related > 0.2
