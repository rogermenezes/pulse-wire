import json
import os
import sys

from app.jobs.ingestion import run_ingestion_job


def main() -> int:
    job_type = os.getenv("JOB_TYPE", "ingestion")

    if job_type != "ingestion":
        print(json.dumps({"ok": False, "error": f"Unsupported JOB_TYPE: {job_type}"}))
        return 2

    raw_types = os.getenv("SOURCE_TYPES", "").strip()
    source_types = [item.strip() for item in raw_types.split(",") if item.strip()] or None

    result = run_ingestion_job(source_types=source_types)
    print(json.dumps({"ok": True, "job_type": job_type, "source_types": source_types or [], "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
