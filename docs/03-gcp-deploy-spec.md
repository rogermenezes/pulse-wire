# Codex Prompt: Build a GCP-Ready News Aggregator (Next.js + FastAPI + Postgres + Redis)

You are building a production-minded news aggregator web application that is designed for local development first, but with a deployment path that maps cleanly to Google Cloud.

The goal is to avoid a local architecture that needs to be reworked later. The development setup should mirror the eventual Google Cloud deployment model as closely as practical.

## Product Goal

Build a modern news aggregator website that:

1. Ingests content from multiple sources such as X/Twitter handles (where legally and technically permitted), Reddit, Discord communities (where permitted), RSS feeds, and other public news sources.
2. Normalizes and stores raw items.
3. Clusters related items into story groups.
4. Uses LLM APIs (OpenAI and/or Anthropic) to summarize evolving stories.
5. Presents a polished, fast, news-oriented reader experience.
6. Supports categories such as Breaking News, Sports, AI and Tech, Finance, World, and Business.

## Core Stack

Use the following stack exactly:

- Frontend: Next.js (latest stable, App Router, TypeScript)
- Backend API: FastAPI (Python 3.12)
- Database: PostgreSQL
- Cache / queue / job coordination: Redis
- Styling: Tailwind CSS
- ORM: SQLAlchemy 2.x with Alembic migrations
- Frontend data fetching: server components where useful + client components only when needed
- Containerization: Docker for every service
- Local orchestration: Docker Compose
- Deployment target: Google Cloud

## Deployment Target on Google Cloud

The codebase and local setup should be designed to deploy to Google Cloud using this mapping:

- Next.js frontend -> Cloud Run service
- FastAPI API -> Cloud Run service
- Background workers / scheduled crawlers -> Cloud Run jobs (or a dedicated worker service if needed)
- PostgreSQL -> Cloud SQL for PostgreSQL
- Redis -> Memorystore for Redis
- Container images -> Artifact Registry
- CI/CD -> Cloud Build
- Secrets -> Secret Manager
- Static assets / backup exports -> Cloud Storage
- Logging / monitoring -> Cloud Logging and Cloud Monitoring

Design the app so that each service is containerized and stateless, because Cloud Run expects containerized stateless workloads, while one-off background tasks fit naturally into Cloud Run Jobs.

## Important Engineering Principle

The local development environment should feel like a smaller version of production:

- Same services
- Same environment variable structure
- Same container entrypoints
- Same health checks
- Same migration flow
- Same separation between web, API, worker, database, and Redis

Do not build a monolith that tightly couples everything together.

## Architecture Requirements

Create a monorepo with clear boundaries:

- `apps/web` -> Next.js app
- `apps/api` -> FastAPI app
- `apps/worker` -> Python worker processes for crawling, clustering, summarization
- `packages/shared-types` -> shared TypeScript types / API contracts where helpful
- `infra/docker` -> Dockerfiles and compose files
- `infra/cloudbuild` -> Cloud Build configs
- `infra/scripts` -> local bootstrap, seed, migration, and deploy helper scripts
- `docs` -> setup and architecture docs

### Logical flow

1. Crawlers pull items from allowed sources.
2. Raw content is normalized into a canonical format.
3. Duplicate detection and clustering combine related posts/articles.
4. LLM summarization produces:
   - headline
   - short summary
   - longer summary
   - bullet timeline
   - confidence / coverage notes
5. API serves clustered stories and source items.
6. Web UI renders category feeds and story pages.

## Data Model

Implement database models for at least:

- `sources`
  - id
  - type (rss, reddit, discord, twitter, website, other)
  - name
  - canonical_url
  - enabled
  - polling_interval_seconds
  - metadata_json
  - created_at
  - updated_at

- `raw_items`
  - id
  - source_id
  - external_id
  - url
  - title
  - author
  - published_at
  - fetched_at
  - content_text
  - content_html (nullable)
  - language
  - metadata_json
  - content_hash
  - embedding_status

- `story_clusters`
  - id
  - cluster_key
  - category
  - primary_headline
  - summary_short
  - summary_long
  - status
  - first_seen_at
  - last_updated_at
  - importance_score
  - freshness_score

- `cluster_items`
  - id
  - cluster_id
  - raw_item_id
  - relevance_score
  - is_primary

- `summaries`
  - id
  - cluster_id
  - provider (openai, anthropic)
  - model_name
  - prompt_version
  - summary_short
  - summary_long
  - bullets_json
  - generated_at

- `categories`
  - id
  - slug
  - display_name
  - sort_order

- `story_category_map`
  - id
  - cluster_id
  - category_id

- `crawl_runs`
  - id
  - source_id
  - started_at
  - completed_at
  - status
  - items_fetched
  - error_message

## Local Development Environment (GCP-Aligned)

Set up local development with Docker Compose.

### Required local services

- `web` (Next.js)
- `api` (FastAPI)
- `worker` (Python worker)
- `scheduler` (optional lightweight process that triggers crawl jobs locally)
- `postgres`
- `redis`

### Docker requirements

- Each app gets its own Dockerfile.
- Use multi-stage builds where practical.
- Containers must run via explicit commands that can also be reused in Cloud Run.
- Add health endpoints:
  - Next.js: `/api/health` or equivalent
  - FastAPI: `/healthz`
- FastAPI must bind to `0.0.0.0` and respect a `PORT` environment variable for Cloud Run compatibility.
- Next.js must also respect `PORT`.

### Docker Compose requirements

Create a `docker-compose.yml` that:

- Starts Postgres and Redis first
- Builds and runs web, api, and worker
- Mounts source code for local development where useful
- Uses named volumes for Postgres persistence
- Exposes:
  - web on `3000`
  - api on `8000`
  - postgres on `5432`
  - redis on `6379`
- Includes environment files for local-only values
- Supports live reload for both Next.js and FastAPI

### Environment variable design

Use a consistent `.env` strategy:

- `.env.example` committed
- `.env.local` ignored
- service-specific env loading where needed

Define variables such as:

- `APP_ENV`
- `WEB_PORT`
- `API_PORT`
- `DATABASE_URL`
- `REDIS_URL`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `NEXT_PUBLIC_API_BASE_URL`
- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GCS_BUCKET_NAME`
- `SECRET_PROVIDER`

Structure env usage so local development can use plain env vars, while production can inject them from Secret Manager.

## Google Cloud Readiness Constraints

The implementation must be written so deployment to Cloud Run is straightforward.

### Cloud Run compatibility

- No reliance on local disk for durable state.
- Use ephemeral disk only for temporary files.
- All persistent state goes to Postgres, Redis, or Cloud Storage.
- Services must start quickly.
- Honor the `PORT` environment variable.
- All containers must be runnable with a single process per container.
- Avoid background threads inside the web container for long-running crawl logic.

### Cloud SQL readiness

- Keep database access behind SQLAlchemy.
- Use Alembic for all schema changes.
- Provide a migration command that can run in CI/CD or as a one-off task.
- Make connection settings configurable so local can use standard TCP and production can later be configured for Cloud SQL connection strategy.

### Redis readiness

- Use Redis for:
  - caching category feeds
  - deduplication locks
  - simple job queue or task coordination
  - rate-limit bookkeeping
- Abstract Redis access behind a small internal service layer so local Redis can later be swapped to managed Memorystore without code changes.

## API Requirements

FastAPI should provide endpoints such as:

- `GET /healthz`
- `GET /api/v1/stories`
- `GET /api/v1/stories/{id}`
- `GET /api/v1/categories`
- `GET /api/v1/categories/{slug}/stories`
- `POST /api/v1/admin/crawl/run`
- `POST /api/v1/admin/clusters/rebuild`
- `POST /api/v1/admin/summaries/regenerate`

Include:

- Pydantic models
- structured error responses
- pagination
- sorting by recency and importance
- filtering by category and time window

## Ingestion Requirements

Implement source adapters with a plugin pattern.

Each adapter should:

- fetch source data
- normalize into a canonical schema
- compute a stable content hash
- persist items idempotently
- emit signals / tasks for clustering

Start with these adapters first:

1. RSS feeds
2. Reddit (public subreddits)
3. Generic web feed adapter

Design interfaces so other adapters can be added later:

- Discord ingestion (subject to server permissions and policy)
- X/Twitter ingestion (subject to API access, terms, and cost)

Do not hardcode assumptions that every source has the same metadata.

## Clustering Requirements

Implement a pragmatic clustering approach for MVP:

- dedupe exact duplicates by hash
- near-duplicate detection via normalized title similarity
- optional embeddings-based similarity for richer grouping
- a background job that periodically rebuilds or updates clusters

Store the cluster state in Postgres.

## LLM Summarization Requirements

Support provider abstraction:

- OpenAI
- Anthropic

Build an internal summarization service that can:

- generate short and long summaries
- produce bullet points
- cite source count and recency metadata
- regenerate summaries when new items are added to a cluster

Add guardrails:

- do not overstate facts
- indicate uncertainty when source agreement is weak
- include timestamps in story metadata

## Frontend UX Requirements

The Next.js app should feel like a modern news product.

Pages:

- Home page: top stories across categories
- Category pages: Breaking News, Sports, AI and Tech, Finance, World, Business
- Story detail page: cluster headline, summaries, key updates, linked source items
- Search page
- Admin page (simple internal UI for triggering ingestion jobs)

UX expectations:

- fast first load
- server-rendered category pages for SEO and speed
- card-based feed layout
- mobile responsive design
- time-ago labels plus exact timestamps
- clear separation between story summaries and raw source links
- ability to sort by newest or most important

## Security and Secrets

- Never commit secrets.
- Use `.env.example` only for placeholders.
- Add code paths that can read from environment variables cleanly.
- Prepare the code so production secrets can later come from Secret Manager.
- Basic admin endpoints should be protected by a simple auth mechanism in MVP.

## CI/CD Requirements

Provide Google Cloud-oriented CI/CD artifacts:

- Cloud Build config(s) to:
  - build web image
  - build api image
  - build worker image
  - push images to Artifact Registry
- Optional deploy scripts for Cloud Run services and jobs
- Separate configs for preview vs production if helpful

The generated repository should include:

- `cloudbuild.web.yaml`
- `cloudbuild.api.yaml`
- `cloudbuild.worker.yaml`

## Developer Experience

The repository should be easy for a developer to start locally.

Include:

- `make dev` or equivalent command to start everything
- `make migrate`
- `make seed`
- `make test`
- `make lint`
- `make format`

Also include a high-quality `README.md` with:

1. local prerequisites
2. how to start with Docker Compose
3. how to run database migrations
4. how to seed sample data
5. how to add RSS feeds
6. how to configure LLM providers
7. how the GCP deployment mapping works

## What to Generate

Generate a working starter repository with:

- the full monorepo structure
- Dockerfiles for each service
- Docker Compose setup
- Next.js app scaffold with category pages and story cards
- FastAPI app scaffold with models, migrations, and sample endpoints
- Worker scaffold for crawl / cluster / summarize jobs
- Redis integration
- Postgres integration
- example seed data
- `.env.example`
- Cloud Build YAML files
- scripts for local setup and basic deploy preparation
- a clear README

## Implementation Priorities

Prioritize in this order:

1. Local developer experience
2. Clean boundaries between services
3. GCP deployment compatibility
4. MVP ingestion and browsing flow
5. Future extensibility

## Non-Goals for First Version

Do not overbuild in v1:

- no need for advanced personalization yet
- no need for full auth system for public users yet
- no need for a heavy event bus in the first version
- no need for Kubernetes setup yet

## Output Style

When generating code:

- be concrete, not vague
- create actual files, not just descriptions
- include comments where architecture choices matter
- prefer simple reliable patterns over clever abstractions
- ensure the project can run locally with Docker Compose before any cloud deployment

