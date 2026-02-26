# Build a News Aggregator Web App

You are an expert full-stack engineer. Build an MVP-to-production-ready web application called **PulseWire**: a modern news aggregator that ingests content from multiple sources, groups related reports into stories, summarizes them with LLMs, and presents them in a clean, fast, highly browseable user experience.

## Objective

Create a website that helps readers quickly understand the newest happenings of the day by collecting posts and articles from multiple public sources, clustering similar items into a single story, and generating concise summaries.

The app should feel like a blend of:
- a real-time feed reader
- a topic-aware news homepage
- an AI-powered summary and story discovery layer

## Core Product Requirements

### 1) Content ingestion
Build ingestion pipelines for public and permitted sources, including:
- RSS feeds from major news publishers
- Reddit (specific subreddits manually configured by the app owner)
- X / Twitter public content from specific handles manually configured by the app owner, where legally and technically allowed via official APIs or approved providers
- Discord channels/servers where the app owner has explicit access and API permissions
- YouTube channels or handles manually configured by the app owner
- Optional future connectors: Hacker News, Mastodon, Bluesky, blogs, newsletters

Important:
- The app does not need to discover sources automatically. All tracked sources (Twitter handles, subreddits, YouTube channels, Discord servers, RSS feeds, etc.) will be manually provided and curated by the app owner through configuration or an admin UI.
- Use official APIs where possible.
- Respect platform rate limits, terms of service, robots.txt, and authentication requirements.
- Do not implement shady scraping if it violates terms or is brittle.
- Design ingestion connectors behind a common interface so new sources can be added easily.

Each ingested item should be normalized into a canonical format with fields such as:
- `id`
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
- embed title + body
- use a similarity threshold for candidate cluster assignment
- use recency weighting so old and new unrelated stories do not merge
- maintain cluster states such as `breaking`, `developing`, `stable`, `archived`

### 3) LLM summarization
For each story cluster, generate AI summaries using pluggable LLM providers.

Support:
- OpenAI APIs
- Anthropic APIs
- abstraction so more providers can be added later

Generate:
- a 1-2 sentence short summary
- a longer summary with key developments
- bullet points for what changed recently
- optional "why this matters" section
- optional confidence or source diversity indicator

Requirements:
- Ground the summary in the underlying source items
- Prefer the most recent and high-signal sources
- Avoid hallucinations; only summarize what is supported by the cluster content
- Keep citation metadata internally so the UI can link back to original sources
- Cache summaries and re-run only when a cluster materially changes

### 4) Categorization
Support top-level categories such as:
- Breaking News
- World
- Sports
- AI and Tech
- Finance
- Business
- Science
- Entertainment

Implement either:
- rule-based tagging + source-based hints + keyword models
- or an LLM/ML classifier with fallback heuristics

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
- timeline of updates
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

## Technical Requirements

### Preferred stack
Use the following unless there is a strong reason to improve it:
- **Frontend:** Next.js (App Router), React, TypeScript, Tailwind CSS
- **Backend:** Next.js API routes or a separate Node.js service using TypeScript
- **Database:** PostgreSQL
- **Cache / queue:** Redis
- **ORM:** Prisma
- **Background jobs:** BullMQ or equivalent
- **Embeddings:** OpenAI embeddings or a pluggable embeddings layer
- **Auth:** optional for MVP, but structure for future accounts
- **Deployment:** Vercel for frontend, Railway/Fly.io/Render for backend workers, managed Postgres and Redis

If a Python service is better for ingestion or clustering, it is acceptable to split architecture into:
- TypeScript web app + API
- Python worker service for ingestion/clustering/summarization

But keep the developer experience simple.

### Architecture
Design the codebase with clear modules:
- `apps/web` for frontend
- `apps/api` or API routes for app backend
- `workers/ingestion`
- `workers/clustering`
- `workers/summarization`
- `packages/shared` for shared types/utilities

Use clean interfaces for connectors:
- `SourceConnector`
- `fetchLatest()`
- `normalize()`
- `validate()`

Also define a clear manual source configuration model, for example:
- `config/sources.json` or database-backed `sources` records
- fields like `source_type`, `handle_or_identifier`, `display_name`, `enabled`, `category_hints`, `poll_interval`, `auth_reference`
- support enabling/disabling specific sources without redeploying if using admin config

### Data model
At minimum, create schemas/tables for:
- `sources`
- `source_lists` or `source_groups` (optional but recommended for organizing manually curated feeds)
- `source_items`
- `story_clusters`
- `cluster_items`
- `summaries`
- `categories`
- `tags`
- `ingestion_runs`

Include important indexes for:
- published time
- category
- cluster id
- source type
- dedupe hashes

### Background processing
Implement scheduled jobs to:
- fetch new items on a cadence
- normalize and store content
- dedupe
- cluster new items
- regenerate summaries for changed clusters
- mark stale clusters archived

Use idempotent jobs and retry handling.

### API design
Create a clean API for the frontend. Example endpoints:
- `GET /api/stories?category=breaking&limit=20`
- `GET /api/stories/:id`
- `GET /api/categories`
- `GET /api/search?q=...`
- `POST /api/admin/reingest`

Return typed JSON responses.

## Feature Scope

### MVP
The first version must include:
- RSS ingestion
- Reddit ingestion
- support for manually curated source lists (Twitter handles, subreddits, YouTube channels, Discord sources, RSS feeds)
- configuration-driven source onboarding, with a simple seed file and optional admin CRUD UI later
- clustering
- AI summaries
- category pages
- homepage with latest + breaking
- story details page
- search
- basic admin controls (protected by env-based secret or simple auth)

### Phase 2
Then design room for:
- Discord ingestion
- X / Twitter ingestion
- user personalization
- bookmarks / saved stories
- newsletter digest
- push notifications
- region/language preferences
- trending detection
- source credibility scoring

## Quality Bar

### Code quality
- Use TypeScript end to end where practical
- Strong typing for all DTOs and database models
- Keep code modular and maintainable
- Add clear comments where logic is non-obvious
- Provide environment variable examples
- Avoid hard-coded secrets

### Testing
Include:
- unit tests for normalization and clustering utilities
- integration tests for key API endpoints
- basic UI smoke tests for critical pages

### Observability
Include:
- structured logging
- ingestion job status tracking
- error handling and retries
- admin-visible job failures if feasible

## Security and Compliance

- Respect source platform policies and API contracts
- Do not scrape private or unauthorized data
- Add rate limiting on public endpoints
- Validate and sanitize all external content
- Protect admin endpoints
- Keep provider API keys in environment variables

## Deliverables

Produce the following in the repository:

1. A working implementation of the MVP
2. A well-structured README with setup instructions
3. `.env.example` with all needed variables
4. Seed data / sample source configuration
5. Database schema and migrations
6. Background worker setup
7. Clear instructions for running locally
8. A short architecture note explaining ingestion, clustering, summarization, and rendering flow

## UX Guidance

Design style should be:
- elegant
- minimal
- information dense without feeling cluttered
- similar in polish to modern media dashboards

Suggested UI pieces:
- sticky header
- category pill navigation
- featured breaking story hero section
- stacked or card-based story list
- source count indicator (for example: "12 sources")
- freshness badges
- expandable source timeline
- compact mobile cards

## Suggested Implementation Notes

- Use server-side rendering or hybrid rendering for fast first load and SEO
- Use incremental refresh / revalidation where appropriate
- Cache expensive queries
- Use a ranking heuristic for homepage ordering based on recency, source diversity, engagement, and category priority
- Separate ingestion timestamps from publication timestamps
- Build the system so connectors can fail independently without taking down the site

## Nice-to-have Enhancements

If time permits, add:
- source filtering
- duplicate source collapse in UI
- confidence meter based on source diversity and agreement
- a "what changed" diff between earlier and later summaries
- image thumbnails for stories when available
- trending keywords panel
- daily digest generation

## What to output while coding

When implementing this project:
- first propose the folder structure
- then implement the database schema
- then build ingestion connectors
- then clustering and summarization pipeline
- then API routes
- then frontend pages and components
- then tests and README

As you work:
- explain tradeoffs briefly when choosing architecture
- keep the app runnable at each milestone
- prefer practical, production-sensible decisions over overengineering

## Final instruction

Build this as if it could become a real product. Prioritize:
1. correctness
2. extensibility
3. UX polish
4. operational simplicity

If a requirement is ambiguous, choose the simplest solution that preserves a clean path to future expansion.
