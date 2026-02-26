from fastapi import APIRouter, Header, HTTPException

from app.core.config import settings
from app.schemas import ReingestRequest, ReingestResponse
from app.services.store import load_curated_sources

router = APIRouter(prefix="/v1/admin", tags=["admin"])


def verify_admin_token(authorization: str | None) -> None:
    expected = f"Bearer {settings.api_admin_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/reingest", response_model=ReingestResponse)
def trigger_reingest(payload: ReingestRequest, authorization: str | None = Header(default=None)) -> ReingestResponse:
    verify_admin_token(authorization)
    curated = load_curated_sources()
    selected_types = set(payload.source_types or [])

    eligible = [
        source for source in curated if source["enabled"] and (not selected_types or source["source_type"] in selected_types)
    ]

    return ReingestResponse(
        queued=True,
        message=f"Queued ingestion scaffold for {len(eligible)} manually curated source(s).",
    )
