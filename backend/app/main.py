from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_admin import router as admin_router
from app.api.routes_health import router as health_router
from app.api.routes_public import router as public_router
from app.core.config import settings
from app.db.bootstrap import init_db, seed_categories, seed_sources
from app.db.session import SessionLocal

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    with SessionLocal() as db:
        seed_categories(db)
        seed_sources(db)


app.include_router(health_router)
app.include_router(public_router)
app.include_router(admin_router)
