# Build a News Aggregator Web App (Next.js + FastAPI + Postgres + Redis)

You are an expert full-stack engineer. Build an MVP-to-production-ready web application called **PulseWire**: a modern news aggregator that ingests content from multiple public sources, groups related reports into stories, summarizes them with LLMs, and presents them in a clean, fast, highly browseable user experience.

This implementation must use a **split architecture**:
- **Next.js** for the web application and reader-facing API layer
- **FastAPI** for ingestion, clustering, summarization, and admin/internal APIs
- **PostgreSQL** as the system of record
- **Redis** for caching, rate limiting, scheduling support, and job queues

Use practical, production-sensible defaults. Optimize for a strong MVP that can scale.

---

## Objective

Create a website that helps readers quickly understand the newest happenings of the day by:
- collecting posts and articles from multiple public sources
- normalizing and deduplicating them
- clustering related reports into a single story
- generating concise LLM-powered summaries
- presenting them in a polished, fast, category-driven UX

The app should feel like a blend of:
- a real-time feed reader
- a topic-aware news homepage
- an AI-powered summary and story discovery layer

---

## Core Product Requirements

### 1) Content ingestion
Build ingestion pipelines for public and permitted sources, including:
- RSS feeds from major news publishers
- Reddit (subreddits, posts, comments where appropriate via official APIs)
- X / Twitter public content where legally and technically allowed via official APIs or approved providers
- Discord channels/servers where the app owner has explicit access and API permissions
- Optional future connectors: YouTube channels, Hacker News, Mastodon, Bluesky, blogs, newsletters

Important:
- Use official APIs where possible.
- Respect platform rate limits, terms of service, robots.txt, and authentication requirements.
- Do not implement unauthorized or brittle scraping that violates platform rules.
- Design ingestion connectors behind a common interface so new sources can be added easily.
- Make connectors independently deployable and fault-tolerant.

Each ingested item should be normalized into a canonical format with fields such as:
- `id`
- `external_id`
- `source_type` (rss, reddit, twitter, discord, etc.)
- `source_name`
- `author`
- `title`
- `body`
- `url`
- `published_at`
- `fetched_at`
- `language`
- `engagement` (likes, comments, shares, upvotes if available)
- `category_candidates`
- `media` (optional image/video metadata)
- `raw_payload`
- `content_hash`

### 2) Story clustering
Multiple posts about the same event should be grouped into a single story cluster.

Implement a clustering pipeline that:
- creates embeddings for each content item
- uses semantic similarity plus time proximity and keyword overlap
- assigns items into story clusters
- allows incremental reclustering as new items arrive
- maintains a representative headline and a list of source items per cluster

Suggested logic:
- deduplicate exact or near-exact content first
- embed `title + body`
- use a similarity threshold for candidate cluster assignment
- use recency weighting so old and new unrelated stories do not merge
- maintain cluster states such as `breaking`, `developing`, `stable`, `archived`

### 3) LLM summarization
For each story cluster, generate AI summaries using pluggable LLM providers.

Support:
- OpenAI APIs
- Anthropic APIs
- an internal provider abstraction so more vendors can be added later

Generate:
- a 1-2 sentence short summary
- a longer summary with key developments
- bullet points for what changed recently
- optional "why this matters" section
- optional confidence or source diversity indicator

Requirements:
- Ground the summary in the underlying source items.
- Prefer the most recent and highest-signal sources.
- Avoid hallucinations; only summarize what is supported by the cluster content.
- Keep citation metadata internally so the UI can link back to original sources.
- Cache summaries and re-run only when a cluster materially changes.
- Preserve prior summary versions for audit/debugging when useful.

### 4) Categorization
Support top-level categories such as:
- Breaking News
- World
- US
- Politics
- Sports
- AI and Tech
- Finance
- Business
- Science
- Entertainment

Implement either:
- rule-based tagging + source-based hints + keyword models
- or an ML / LLM classifier with heuristic fallback

Each story can belong to one primary category and multiple secondary tags.

### 5) User experience
Build a polished, modern UX focused on fast scanning and discovery.

The homepage should include:
- a top navigation bar
- category tabs
- a "Latest" feed
- a "Breaking" section
- a story card grid or feed
- timestamps like "5 min ago"
- source badges (Reddit, Reuters, X, etc.)
- story cluster cards that expand into detail views

Story detail pages should include:
- the generated summary
- a timeline of updates
- grouped source links
- related stories
- category tags
- refresh / updated time

UX expectations:
- clean and modern visual design
- responsive layout for desktop and mobile
- excellent readability and spacing
- skeleton loading states
- empty/error states
- dark mode support
- fast page loads
- SEO-friendly story pages

---

## Required Technology Stack

### Web app
Use:
- **Next.js 15+** with App Router
- **React**
- **TypeScript**
- **Tailwind CSS**
- **Server Components by default**, with client components only where needed

Next.js responsibilities:
- render the public website
- provide category pages, story pages, search UI, and homepage
- handle SEO metadata, Open Graph tags, and sitemap generation
- call FastAPI internal APIs for data
- optionally expose a minimal BFF layer for browser-safe calls if needed

### Backend services
Use:
- **FastAPI** for backend services
- **Python 3.12+**
- **Pydantic** for request/response models
- **SQLAlchemy 2.x** (or SQLModel if you strongly prefer it)
- **Alembic** for migrations
- **httpx** for async HTTP clients

FastAPI responsibilities:
- source ingestion connectors
- normalization and deduplication
- clustering pipeline
- summarization orchestration
- search endpoints / internal data APIs
- admin and health endpoints
- background job dispatch and workers

### Data and infrastructure
Use:
- **PostgreSQL** as the primary database
- **Redis** for:
  - queueing and lightweight job coordination
  - short-lived cache entries
  - rate limiting counters
  - recent-feed cache / hot story cache
- **pgvector** in Postgres for embeddings storage and similarity search (preferred)

### Background jobs
Use Python-based workers with Redis-backed queueing.

Preferred options:
- **RQ** or **ARQ** for simple Redis-native jobs
- Celery is acceptable only if justified, but prefer lower operational complexity

Workers should process:
- ingestion jobs
- dedupe jobs
- clustering jobs
- summarization jobs
- stale cluster archival jobs

### Deployment assumptions
Target a simple production setup:
- **Next.js** deployed separately (for example on Vercel or a container platform)
- **FastAPI** as a containerized service
- **Worker** as one or more containerized processes
- managed **Postgres**
- managed **Redis**

Keep the system deployable via Docker Compose locally and easily portable to cloud.

---

## Architecture Requirements

Design this as a small monorepo or clearly organized multi-service repository.

Suggested structure:

```text
pulsewire/
  apps/
    web/                      # Next.js app
  services/
    api/                      # FastAPI app
    worker/                   # Python worker entrypoints
  packages/
    shared-types/             # Optional TS shared contracts/types
  infra/
    docker/                   # Dockerfiles, compose, local infra helpers
  docs/
  README.md
```

A more detailed layout is encouraged:

```text
apps/web/
  app/
    page.tsx
    breaking/page.tsx
    category/[slug]/page.tsx
    story/[id]/page.tsx
    search/page.tsx
  components/
  lib/
    api-client.ts
    formatters.ts
  styles/

services/api/
  app/
    main.py
    api/
      routes_public.py
      routes_admin.py
      routes_health.py
    core/
      config.py
      logging.py
      security.py
    db/
      models.py
      session.py
      migrations/
    schemas/
    services/
      ingestion/
        base.py
        rss.py
        reddit.py
        twitter.py
        discord.py
      clustering/
      summarization/
      categorization/
      ranking/
      search/
    jobs/
    utils/

services/worker/
  worker.py
  tasks/
    ingest.py
    cluster.py
    summarize.py
    cleanup.py
```

### Service boundaries
- **Next.js** should not perform crawling, clustering, or LLM orchestration.
- **FastAPI** should own business logic and data access.
- **Workers** should execute heavy background tasks.
- The browser should never directly hold privileged provider credentials.

### Communication model
- Next.js calls FastAPI over HTTP for story/category/search data.
- Worker processes share the same Postgres + Redis infrastructure as FastAPI.
- Internal APIs can be protected with a service token.
- Public routes should be read-only and cache-friendly.

---

## Data Model

At minimum, create schemas/tables for:
- `sources`
- `source_items`
- `story_clusters`
- `cluster_items`
- `summaries`
- `categories`
- `story_tags`
- `ingestion_runs`
- `job_runs` (optional but recommended)

### Suggested table details

#### `sources`
Store source configuration:
- id
- source_type
- name
- external_ref
- url
- enabled
- polling_interval_seconds
- auth_config (JSON where applicable)
- created_at
- updated_at

#### `source_items`
Store normalized ingested content:
- id
- source_id
- external_id
- author
- title
- body
- canonical_url
- published_at
- fetched_at
- language
- engagement_json
- media_json
- raw_payload_json
- content_hash
- embedding (vector via pgvector if using inline storage)
- dedupe_key
- created_at

#### `story_clusters`
Store cluster metadata:
- id
- slug
- headline
- short_headline
- primary_category_id
- status
- representative_item_id
- first_seen_at
- last_updated_at
- item_count
- source_count
- ranking_score
- created_at
- updated_at

#### `cluster_items`
Join table:
- cluster_id
- source_item_id
- relevance_score
- is_primary
- added_at

#### `summaries`
Store generated summaries:
- id
- cluster_id
- provider
- model
- short_summary
- long_summary
- changes_bullets
- why_it_matters
- source_snapshot_json
- summary_version
- generated_at
- invalidated_at (nullable)

### Indexes
Include important indexes for:
- `source_items(published_at desc)`
- `source_items(content_hash)`
- `source_items(dedupe_key)`
- `story_clusters(primary_category_id, last_updated_at desc)`
- `story_clusters(status, ranking_score desc)`
- `cluster_items(cluster_id)`
- vector similarity index for embeddings if used

### Migration requirements
- Use Alembic migrations.
- Include an initial migration and at least one realistic follow-up migration example.
- Seed the category table.

---

## Ingestion and Processing Pipeline

Implement the backend as a sequence of idempotent steps.

### Step 1: Fetch
- Poll enabled sources on a schedule.
- Fetch latest items based on source-specific logic.
- Store raw responses for debugging where appropriate.

### Step 2: Normalize
- Convert all source-specific payloads into a common canonical schema.
- Normalize timestamps, URLs, usernames, and engagement metrics.
- Strip noisy markup.

### Step 3: Dedupe
- Use exact dedupe with canonical URL and `content_hash`.
- Add near-duplicate heuristics for repeated cross-posts.
- Avoid creating duplicate source items if the same external item is seen again.

### Step 4: Embed + cluster
- Create embeddings for new or materially changed items.
- Search recent candidate clusters by vector similarity + recency.
- Attach to an existing cluster when confidence is high.
- Create a new cluster otherwise.
- Recompute representative headline and ranking metadata.

### Step 5: Categorize
- Assign primary category and supporting tags.
- Prefer deterministic rules for the MVP, with optional ML upgrade path.

### Step 6: Summarize
- Trigger summarization only for new or materially changed clusters.
- Cache the latest valid summary.
- Track summary version history.

### Step 7: Rank for display
Rank stories for homepage/category views using a heuristic that combines:
- recency
- source diversity
- number of corroborating items
- engagement signals where available
- category weighting (for example, Breaking gets a boost)

---

## API Requirements (FastAPI)

Create a clean API consumed by Next.js.

### Public endpoints
Examples:
- `GET /v1/stories?category=breaking&limit=20&cursor=...`
- `GET /v1/stories/{story_id}`
- `GET /v1/categories`
- `GET /v1/search?q=...`
- `GET /v1/breaking`
- `GET /v1/latest`

### Admin/internal endpoints
Examples:
- `POST /v1/admin/reingest`
- `POST /v1/admin/recluster/{story_id}`
- `POST /v1/admin/resummarize/{story_id}`
- `GET /v1/admin/jobs`
- `GET /healthz`
- `GET /readyz`

### API behavior
- Use typed Pydantic response models.
- Support cursor pagination for feeds.
- Return timestamps in ISO 8601 UTC format.
- Add caching headers on public GET endpoints where sensible.
- Rate-limit admin endpoints.
- Protect admin routes with a simple token for MVP.

### Example response shape
Use stable, typed JSON contracts similar to:

```json
{
  "items": [
    {
      "id": "story_123",
      "headline": "Major AI model release triggers industry reaction",
      "short_summary": "Several sources report...",
      "primary_category": "AI and Tech",
      "status": "breaking",
      "source_count": 12,
      "last_updated_at": "2026-02-26T10:15:00Z"
    }
  ],
  "next_cursor": "..."
}
```

---

## Frontend Requirements (Next.js)

Build a polished, modern news-reading experience.

### Pages
Implement:
- homepage
- category page
- story detail page
- search results page
- optional lightweight admin page for job status

### Rendering strategy
Use:
- Server Components for main data rendering
- streaming / loading UI where useful
- route segment loading states
- cache/revalidation strategically for public pages

Recommended approach:
- homepage and category pages use server-side data fetches
- story pages are SEO-first and fast on initial load
- incremental revalidation or short cache windows for fresh content

### UI elements
Include:
- sticky header
- category pill navigation
- featured breaking story hero section
- story cards with summary, freshness, and source count
- source badges
- related stories module
- timeline of updates in story detail view
- responsive mobile cards
- dark mode

### UX quality bar
Design style should be:
- elegant
- minimal
- information-dense without feeling cluttered
- comparable in polish to modern media dashboards

Avoid visual noise and excessive animations.

---

## Caching and Performance

### Redis usage
Use Redis for:
- hot feed cache (homepage, breaking, category summaries)
- short-lived story detail cache
- request-level rate limiting
- job queueing / retry bookkeeping

### Postgres usage
Use Postgres for:
- authoritative story data
- historical summaries
- clustering relationships
- source/item history

### Performance goals
Aim for:
- fast first contentful render on public pages
- efficient cursor pagination
- background processing isolated from request paths
- graceful degradation if one connector fails

Do not block page rendering on live summarization.
Always serve the latest completed summary and refresh asynchronously.

---

## Security and Compliance

- Respect platform policies and API contracts.
- Do not scrape private or unauthorized data.
- Keep all provider API keys in environment variables.
- Protect admin endpoints.
- Validate and sanitize all external content before rendering.
- Add basic abuse protections on public endpoints.
- Ensure browser clients do not access privileged third-party credentials.

---

## Feature Scope

### MVP
The first version must include:
- RSS ingestion
- Reddit ingestion
- manual seed list of sources
- clustering
- AI summaries
- category pages
- homepage with latest + breaking
- story detail page
- search
- basic admin controls (env-based token is acceptable)
- Docker Compose local setup for web + api + worker + postgres + redis

### Phase 2
Design room for:
- Discord ingestion
- X / Twitter ingestion
- user personalization
- bookmarks / saved stories
- newsletter digest
- push notifications
- region/language preferences
- trending detection
- source credibility scoring

---

## Developer Experience Requirements

Produce the following in the repository:

1. A working MVP implementation
2. A clear README with setup instructions
3. `.env.example` files for both web and api services
4. Seed data / sample source configuration
5. Alembic migrations
6. Background worker setup
7. Docker Compose for local development
8. A short architecture note explaining ingestion, clustering, summarization, and rendering flow

### Environment variables
At minimum, account for:
- database connection string
- redis connection string
- OpenAI API key
- Anthropic API key
- internal API base URL
- admin token
- optional source-specific credentials

---

## Testing

Include:
- unit tests for normalization and clustering utilities
- integration tests for key FastAPI endpoints
- basic UI smoke tests for critical Next.js pages
- at least one test for job idempotency or deduplication behavior

Prefer pragmatic coverage over excessive test scaffolding.

---

## Observability

Include:
- structured logging
- ingestion run status tracking
- background job status visibility
- error handling and retries
- health/readiness endpoints
- enough logging to debug connector failures and summary generation issues

A small admin jobs page or admin API output is enough for MVP.

---

## Build Order

When implementing this project, follow this order:

1. Propose the folder structure
2. Set up Docker Compose and local infra
3. Implement the database schema and migrations
4. Build FastAPI config, models, and public endpoints
5. Build ingestion connectors (RSS first, Reddit second)
6. Implement dedupe, embeddings, and clustering
7. Implement summarization pipeline
8. Build the Next.js pages and components
9. Add caching and ranking
10. Add tests and README

As you work:
- explain tradeoffs briefly when choosing architecture
- keep the app runnable at each milestone
- prefer simple, maintainable decisions over overengineering

---

## Final Instruction

Build this as if it could become a real product.
Prioritize:
1. correctness
2. extensibility
3. UX polish
4. operational simplicity

If a requirement is ambiguous, choose the simplest solution that preserves a clean path to future expansion.

In particular:
- keep the business logic in FastAPI
- keep the frontend in Next.js focused on rendering and UX
- keep heavy work in background workers
- use Postgres and Redis intentionally, not gratuitously

The final result should be a realistic, runnable foundation for a production-grade AI-powered news aggregator.
