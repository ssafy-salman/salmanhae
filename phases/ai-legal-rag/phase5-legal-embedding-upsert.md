# Phase 5: Legal Embedding Upsert

## Goal
Connect the legal document ingestion dry-run pipeline to the backend-ai embedding and Supabase pgvector boundaries so prepared legal chunks can be embedded and upserted into `legal_document_chunks`.

## Files
- `backend-ai/tests/test_legal_ingestion_upsert.py` - add offline tests for embedding and upsert orchestration
- `backend-ai/scripts/ingest_legal_docs.py` - add explicit write mode, embedding orchestration, and ingestion summary output
- `backend-ai/app/clients/supabase_client.py` - add a legal chunk upsert method that uses `content_hash` for idempotency
- `phases/ai-legal-rag/phase5-legal-embedding-upsert.md` - phase specification

## Done When
- [ ] Dry-run behavior remains offline and unchanged
- [ ] Write mode embeds each prepared legal chunk through an injectable embedding client
- [ ] Upsert writes include embedding vectors and use `content_hash` as the conflict target
- [ ] Tests pass without live network or database access
- [ ] No news RAG, registry AI analysis, or Spring-side pgvector logic is introduced

## Architecture Rules
- F-3 legal RAG and pgvector work stays in `backend-ai`.
- API keys and database URLs are read from environment-backed settings, never hardcoded.
- Public API contracts are not changed in this phase.
- New feature work follows TDD.

## Implementation Instructions
Write failing tests first with fake embedding and vector clients. Keep the default CLI safe by requiring either `--dry-run` or explicit `--write`; only `--write` may instantiate real clients. Reuse the existing `EmbeddingClient.embed_query` boundary for chunk embeddings and add a narrow Supabase upsert method for `legal_document_chunks`.
