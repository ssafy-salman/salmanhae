# Phase 2: Legal RAG Schema and Ingestion

## Goal
Prepare the legal document chunk model, pgvector database schema, and a deterministic ingestion script foundation for F-3 legal RAG. This phase should make legal corpus ingestion testable without requiring live Supabase writes.

## Files
- `database/migrations/202606220001_create_legal_document_chunks.sql` - pgvector-backed legal chunk table and indexes
- `backend-ai/tests/test_legal_ingestion.py` - tests for legal document loading, chunk normalization, and SQL row preparation
- `backend-ai/scripts/ingest_legal_docs.py` - CLI entrypoint for validating and preparing legal chunks
- `backend-ai/app/rag/chunker.py` - deterministic legal text chunking helpers
- `docs/07_DOMAIN_MODEL.md` - LegalDocumentChunk domain model documentation

## Done When
- [ ] A migration defines `legal_document_chunks` with law metadata, source metadata, content, embedding vector, and indexes
- [ ] Ingestion tests pass without external network or database access
- [ ] `ingest_legal_docs.py --dry-run {input}` validates and summarizes source chunks
- [ ] Domain documentation includes the legal RAG chunk model and MVP scope

## Architecture Rules
- pgvector similarity search and legal RAG data access belong in `backend-ai`.
- API keys, database URLs, and secrets must be supplied from environment variables only.
- MVP F-3 includes 임대차보호법·전세사기특별법 legal RAG only; news RAG and 등기부등본 AI are excluded.
- Data model changes must update `docs/07_DOMAIN_MODEL.md`.

## Implementation Instructions
Write tests first for chunk validation and dry-run behavior. Keep ingestion deterministic and offline in this phase; do not fetch live law text or require Supabase connectivity. Use a JSON source contract that later phases can populate from official legal sources.
