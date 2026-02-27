# PulseWire Dev Quickstart

This guide is for day-to-day local development.

## Prerequisites

- Python 3.12+
- Node.js + npm
- Docker + Docker Compose

## 1) Start infrastructure (Postgres + Redis)

From repo root:

```bash
cd /Users/rmenezes/code/pulse-wire
docker compose up -d postgres redis
```

Check containers:

```bash
docker compose ps
```

## 2) Start backend (FastAPI)

From repo root:

```bash
cd /Users/rmenezes/code/pulse-wire
python3.12 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
```

Start backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If port `8000` is busy, use:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

Backend docs:

- `http://127.0.0.1:8000/docs` (or `8010` if using fallback port)

## 3) Start worker (RQ)

In a new terminal:

```bash
cd /Users/rmenezes/code/pulse-wire/backend
source .venv/bin/activate
python worker.py
```

## 4) Start frontend (Next.js)

Set frontend API target in root `.env`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

If backend is on `8010`, use:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8010
```

Install and run:

```bash
cd /Users/rmenezes/code/pulse-wire/frontend
npm install
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Frontend URL:

- `http://127.0.0.1:3000`

## 5) Useful checks

Backend health:

```bash
curl http://127.0.0.1:8000/healthz
```

Frontend checks:

```bash
cd /Users/rmenezes/code/pulse-wire/frontend
npm run lint
npm run build
```

Backend tests:

```bash
cd /Users/rmenezes/code/pulse-wire
backend/.venv/bin/python -m pytest -q backend
```

## Docker `psql` commands

Open Postgres shell inside container:

```bash
cd /Users/rmenezes/code/pulse-wire
docker compose exec postgres psql -U pulsewire -d pulsewire
```

### Connect from host machine (local `psql` client)

If you have `psql` installed on your host, you can connect directly to the Dockerized Postgres via published port `5432`:

```bash
psql "postgresql://pulsewire:pulsewire@localhost:5432/pulsewire"
```

Equivalent expanded form:

```bash
PGPASSWORD=pulsewire psql -h localhost -p 5432 -U pulsewire -d pulsewire
```

Quick connection test:

```bash
PGPASSWORD=pulsewire psql -h localhost -p 5432 -U pulsewire -d pulsewire -c "SELECT 1;"
```

Common `psql` commands:

```sql
\dt
\d sources
SELECT * FROM sources LIMIT 20;
SELECT * FROM source_items ORDER BY published_at DESC LIMIT 20;
SELECT * FROM story_clusters ORDER BY last_updated_at DESC LIMIT 20;
SELECT * FROM summaries ORDER BY generated_at DESC LIMIT 20;
\q
```

One-off query without interactive shell:

```bash
docker compose exec postgres psql -U pulsewire -d pulsewire -c "SELECT COUNT(*) FROM sources;"
```

## Troubleshooting

- `Address already in use`:
  - Find PID: `lsof -nP -iTCP:8000 -sTCP:LISTEN`
  - Kill PID: `kill <PID>`
  - Or run backend on `8010`.
- Backend DB connection refused:
  - Ensure Postgres is running: `docker compose up -d postgres`
  - Confirm `.env` `DATABASE_URL` points to `localhost:5432` for local backend runs.
- Frontend build shows backend fetch failures:
  - Ensure backend is running and `NEXT_PUBLIC_API_BASE_URL` matches backend port.
