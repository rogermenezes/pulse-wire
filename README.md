# PulseWire MVP Scaffold

First end-to-end scaffold for PulseWire using a split architecture:
- `frontend/`: Next.js (App Router, TypeScript, Tailwind)
- `backend/`: FastAPI (typed API models and routes)
- `infra/`: infra placeholder for future IaC/deploy assets

## What this MVP scaffold includes

- Manually curated source seed file (`backend/app/data/sources.seed.json`) covering RSS, Reddit, X/Twitter, YouTube, and Discord source records.
- Public FastAPI endpoints:
  - `GET /healthz`
  - `GET /readyz`
  - `GET /v1/latest`
  - `GET /v1/breaking`
  - `GET /v1/categories`
  - `GET /v1/stories`
  - `GET /v1/stories/{story_id}`
- Admin FastAPI endpoint:
  - `POST /v1/admin/reingest` (Bearer token protected)
- Next.js homepage and story detail page consuming FastAPI.
- Dockerfiles for both frontend and backend.
- Root `docker-compose.yml` with frontend, backend, Postgres, and Redis.
- Root `.env.example` for local configuration.

## Local setup (without Docker)

1. Copy env file:

```bash
cp .env.example .env
```

2. Run backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

3. Run frontend (new terminal):

```bash
cd frontend
npm install
npm run dev
```

4. Open:
- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

## Local setup (Docker Compose)

```bash
cp .env.example .env
docker compose up --build
```

Services:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Postgres: localhost:5432
- Redis: localhost:6379

## Notes

- This is intentionally the first scaffold milestone; ingestion, clustering, embeddings, DB persistence, migrations, workers, and summarization pipelines are stubbed for the next iteration.
- Source onboarding is configuration-first and manually curated, per product/stack specs.
