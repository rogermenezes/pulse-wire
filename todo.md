# PulseWire Follow-up TODO

## Ingestion Adapters

- [ ] Implement real X/Twitter adapter using official API (OAuth/Bearer token, rate-limit handling, retries).
- [ ] Keep Discord adapter as placeholder until API access scope and server/channel permissions are finalized.
- [ ] Add adapter-level integration tests for live-compatible response fixtures (Reddit/RSS/YouTube/Twitter when implemented).

## Clustering and Relevance

- [ ] Add embeddings-based clustering (`title + body`) with pluggable embedding provider.
- [ ] Store embedding vectors in Postgres (`pgvector`) and use vector similarity for cluster assignment.
- [ ] Combine lexical similarity + vector similarity + recency into a tunable scoring function.
- [ ] Add reclustering job for stale/low-confidence clusters.

## Summarization

- [ ] Improve summary quality prompts and structured outputs (short summary, long summary, changes, why it matters).
- [ ] Add source-citation metadata in summaries for UI traceability.
- [ ] Add per-provider timeout/retry/fallback behavior and summary invalidation rules.

## Source Expansion (Manual Curation)

- [ ] Add more finance sources (subreddits, RSS publishers, verified X handles, YouTube channels).
- [ ] Add more AI/tech sources (high-signal feeds/handles/channels).
- [ ] Add more world/breaking sources with source diversity checks.
- [ ] Add source quality rubric (signal-to-noise, reliability, frequency, duplication risk).

## Data and Jobs

- [ ] Add follow-up Alembic migration examples beyond initial schema.
- [ ] Add job-run table and instrumentation for queue/job observability.
- [ ] Add stale cluster archival/cleanup worker tasks.
- [ ] Add idempotency and duplicate suppression metrics for ingestion runs.

## API + Frontend UX

- [ ] Add category pages/routes beyond homepage query filtering.
- [ ] Add story timeline/“what changed” module in story detail.
- [ ] Add empty/error/loading states for all feed variants.
- [ ] Add admin endpoint/UI for enabling/disabling sources without file edits.

## Testing and Reliability

- [ ] Add pipeline integration tests against temporary Postgres + Redis.
- [ ] Add API contract tests for `/v1/latest`, `/v1/stories`, `/v1/categories`, and admin reingest.
- [ ] Add regression tests for category assignment from source hints.
- [ ] Add CI workflow to run backend tests and frontend lint/build on each PR.
