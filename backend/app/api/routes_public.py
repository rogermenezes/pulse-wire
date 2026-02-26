from fastapi import APIRouter, HTTPException, Query

from app.schemas import CategoriesResponse, StoryDetail, StoryListResponse
from app.services.store import CATEGORIES, seeded_stories

router = APIRouter(prefix="/v1", tags=["public"])


@router.get("/categories", response_model=CategoriesResponse)
def get_categories() -> CategoriesResponse:
    return CategoriesResponse(items=CATEGORIES)


@router.get("/latest", response_model=StoryListResponse)
def get_latest(limit: int = Query(default=20, ge=1, le=50)) -> StoryListResponse:
    stories = seeded_stories()[:limit]
    cards = [story.model_dump(exclude={"long_summary", "sources"}) for story in stories]
    return StoryListResponse(items=cards)


@router.get("/breaking", response_model=StoryListResponse)
def get_breaking(limit: int = Query(default=20, ge=1, le=50)) -> StoryListResponse:
    stories = [story for story in seeded_stories() if story.status == "breaking"][:limit]
    cards = [story.model_dump(exclude={"long_summary", "sources"}) for story in stories]
    return StoryListResponse(items=cards)


@router.get("/stories", response_model=StoryListResponse)
def list_stories(category: str | None = None, limit: int = Query(default=20, ge=1, le=50)) -> StoryListResponse:
    stories = seeded_stories()
    if category:
        stories = [story for story in stories if story.primary_category.lower().replace(" ", "-") == category.lower()]
    cards = [story.model_dump(exclude={"long_summary", "sources"}) for story in stories[:limit]]
    return StoryListResponse(items=cards)


@router.get("/stories/{story_id}", response_model=StoryDetail)
def get_story(story_id: str) -> StoryDetail:
    for story in seeded_stories():
        if story.id == story_id:
            return story
    raise HTTPException(status_code=404, detail="Story not found")
