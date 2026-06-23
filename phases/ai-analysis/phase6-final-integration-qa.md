# Phase 6: Final Integration QA

## Goal
Close F-4 by validating the end-to-end analysis flow across Spring Boot, backend-ai, frontend, and documentation. Keep the scope to MVP price/safety analysis only.

## Files
- `frontend/src/api/chat.test.mjs` - add final contract regression coverage if gaps remain.
- `backend-ai/tests/` - add or adjust final analysis flow tests if gaps remain.
- `backend/src/test/` - add or adjust final Spring chat/analysis contract tests if gaps remain.
- `docs/08_API_SPEC.md` - align frontend-visible F-4 examples if needed.
- `phases/ai-analysis/phase6-final-integration-qa.md` - phase specification.

## Done When
- [x] F-4 chat request/response contract is covered from selected property context through analysisCards.
- [x] Price/safety analysis remains grounded in tool results and excludes MVP-out-of-scope HUG/legal conclusions.
- [x] Frontend-visible API spec matches the implemented request and analysis card response shape.
- [x] Relevant backend, backend-ai, and frontend tests pass or any environment limitation is documented.

## Architecture Rules
- Frontend calls only Spring Boot `/api/v1/chat`.
- Spring Boot does not call an LLM directly.
- FastAPI owns LangGraph intent routing and LLM answer generation.
- MVP scope excludes HUG precision checks, news RAG, WMS layers, and registry-document AI.

## Implementation Instructions
Audit before editing. Prefer regression tests and documentation alignment over feature expansion. Do not add new user-facing flows unless a test or doc mismatch proves they are needed.
