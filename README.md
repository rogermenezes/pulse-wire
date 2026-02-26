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
- Redis-backed queueing (RQ) with a worker process (`backend/worker.py`) for ingestion pipeline execution.
- Postgres-backed persistence for:
  - `sources`
  - `ingestion_runs`
  - `raw_ingested_items`
  - `source_items`
  - `story_clusters`
  - `cluster_items`
  - `summaries`
  - `categories`
  - `story_tags`
- Ingestion adapters:
  - RSS
  - Reddit
  - YouTube
  - Placeholder stubs for X/Twitter and Discord
- Clustering + summarization pipeline hooks (OpenAI/Anthropic + deterministic fallback provider).
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

3. Run worker (new terminal):

```bash
cd backend
source .venv/bin/activate
python worker.py
```

4. Run frontend (new terminal):

```bash
cd frontend
npm install
npm run dev
```

5. Open:
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

- Ingestion/clustering/summarization now run through the admin reingest entrypoint (`POST /v1/admin/reingest`) and queue-backed worker.
- Twitter and Discord adapters remain placeholders (by design in this milestone).
- OpenAI/Anthropic providers are implemented as hooks; without API keys they fall back to deterministic summaries.
- Source onboarding is configuration-first and manually curated, per product/stack specs.
