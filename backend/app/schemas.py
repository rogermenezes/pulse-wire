from datetime import datetime

from pydantic import BaseModel


class Category(BaseModel):
    slug: str
    name: str


class StoryCard(BaseModel):
    id: str
    headline: str
    short_summary: str
    primary_category: str
    status: str
    source_count: int
    last_updated_at: datetime


class StoryListResponse(BaseModel):
    items: list[StoryCard]
    next_cursor: str | None = None


class StorySource(BaseModel):
    source_name: str
    source_type: str
    url: str
    published_at: datetime


class StoryDetail(StoryCard):
    long_summary: str
    sources: list[StorySource]


class CategoriesResponse(BaseModel):
    items: list[Category]


class ReingestRequest(BaseModel):
    source_types: list[str] | None = None


class ReingestResponse(BaseModel):
    queued: bool
    message: str
