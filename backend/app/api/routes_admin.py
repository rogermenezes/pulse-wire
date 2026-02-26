from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import select

from app.core.config import settings
from app.db.models import Source
from app.db.session import SessionLocal
from app.jobs.ingestion import run_ingestion_job
from app.schemas import ReingestRequest, ReingestResponse
from app.services.queue import get_queue

router = APIRouter(prefix="/v1/admin", tags=["admin"])


def verify_admin_token(authorization: str | None) -> None:
    expected = f"Bearer {settings.api_admin_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/reingest", response_model=ReingestResponse)
def trigger_reingest(payload: ReingestRequest, authorization: str | None = Header(default=None)) -> ReingestResponse:
    verify_admin_token(authorization)

    with SessionLocal() as db:
        source_query = select(Source).where(Source.enabled.is_(True))
        selected_types = set(payload.source_types or [])
        if selected_types:
            source_query = source_query.where(Source.source_type.in_(selected_types))
        eligible_count = len(db.scalars(source_query).all())

    try:
        queue = get_queue()
        job = queue.enqueue(run_ingestion_job, source_types=payload.source_types)
        job_id = job.id
    except Exception:
        result = run_ingestion_job(source_types=payload.source_types)
        job_id = f"sync:{result['normalized_count']}"

    return ReingestResponse(
        queued=True,
        message=f"Queued ingestion for {eligible_count} manually curated source(s). job_id={job_id}",
    )
