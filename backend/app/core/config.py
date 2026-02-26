from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PulseWire API"
    app_env: str = "development"
    api_admin_token: str = "change-me"
    frontend_origin: str = "http://localhost:3000"

    database_url: str = "postgresql+psycopg://pulsewire:pulsewire@localhost:5432/pulsewire"
    redis_url: str = "redis://localhost:6379/0"

    reddit_user_agent: str = "pulsewire-bot/0.1"
    ingestion_timeout_seconds: int = 15
    ingestion_default_limit: int = 25

    cluster_similarity_threshold: float = Field(default=0.28, ge=0.0, le=1.0)
    cluster_window_hours: int = 72

    summarization_provider: str = "stub"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-haiku-latest"

    feed_cache_ttl_seconds: int = 45

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
