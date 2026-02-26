from app.services.ingestion.base import SourceConnector
from app.services.ingestion.discord import DiscordConnector
from app.services.ingestion.reddit import RedditConnector
from app.services.ingestion.rss import RSSConnector
from app.services.ingestion.twitter import TwitterConnector
from app.services.ingestion.youtube import YouTubeConnector

CONNECTORS: dict[str, SourceConnector] = {
    "rss": RSSConnector(),
    "reddit": RedditConnector(),
    "youtube": YouTubeConnector(),
    "twitter": TwitterConnector(),
    "discord": DiscordConnector(),
}


def get_connector(source_type: str) -> SourceConnector | None:
    return CONNECTORS.get(source_type)
