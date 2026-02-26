from app.db.session import SessionLocal
from app.services.pipeline import PipelineResult, run_ingestion_pipeline


def run_ingestion_job(source_types: list[str] | None = None) -> dict:
    with SessionLocal() as db:
        result: PipelineResult = run_ingestion_pipeline(db, source_types=source_types)
        return {
            "fetched_count": result.fetched_count,
            "normalized_count": result.normalized_count,
            "clustered_count": result.clustered_count,
        }
