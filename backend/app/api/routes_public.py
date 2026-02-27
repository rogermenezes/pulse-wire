from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas import CategoriesResponse, StoryDetail, StoryListResponse
from app.services.cache import get_cache_json, set_cache_json
from app.services.store import get_categories, get_story_cards, get_story_detail, seeded_stories

router = APIRouter(prefix="/v1", tags=["public"])


@router.get("/categories", response_model=CategoriesResponse)
def categories(db: Session = Depends(get_db)) -> CategoriesResponse:
    cache_key = "public:categories"
    cached = get_cache_json(cache_key)
    if cached:
        return CategoriesResponse(**cached)

    payload = CategoriesResponse(items=get_categories(db))
    set_cache_json(cache_key, payload.model_dump(mode="json"), settings.feed_cache_ttl_seconds)
    return payload


@router.get("/latest", response_model=StoryListResponse)
def get_latest(limit: int = Query(default=20, ge=1, le=50), db: Session = Depends(get_db)) -> StoryListResponse:
    cache_key = f"public:latest:{limit}"
    cached = get_cache_json(cache_key)
    if cached:
        return StoryListResponse(**cached)

    cards = get_story_cards(db, limit=limit)
    if not cards:
        fallback = [story.model_dump(exclude={"long_summary", "sources"}) for story in seeded_stories()[:limit]]
        return StoryListResponse(items=fallback)

    payload = StoryListResponse(items=cards)
    set_cache_json(cache_key, payload.model_dump(mode="json"), settings.feed_cache_ttl_seconds)
    return payload


@router.get("/breaking", response_model=StoryListResponse)
def get_breaking(limit: int = Query(default=20, ge=1, le=50), db: Session = Depends(get_db)) -> StoryListResponse:
    cards = get_story_cards(db, limit=limit, status="breaking")
    if not cards:
        fallback = [story.model_dump(exclude={"long_summary", "sources"}) for story in seeded_stories()[:limit]]
        return StoryListResponse(items=fallback)
    return StoryListResponse(items=cards)


@router.get("/stories", response_model=StoryListResponse)
def list_stories(
    category: str | None = None,
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> StoryListResponse:
    if category and category.lower() == "breaking":
        cards = get_story_cards(db, limit=limit, status="breaking")
        if cards:
            return StoryListResponse(items=cards)

    cards = get_story_cards(db, limit=limit, category_slug=category)
    if cards:
        return StoryListResponse(items=cards)

    if category:
        return StoryListResponse(items=[])

    fallback = [story.model_dump(exclude={"long_summary", "sources"}) for story in seeded_stories()[:limit]]
    return StoryListResponse(items=fallback)


@router.get("/stories/{story_id}", response_model=StoryDetail)
def get_story(story_id: str, db: Session = Depends(get_db)) -> StoryDetail:
    detail = get_story_detail(db, story_id)
    if detail:
        return detail

    for story in seeded_stories():
        if story.id == story_id:
            return story

    raise HTTPException(status_code=404, detail="Story not found")
