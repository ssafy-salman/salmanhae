# Phase 6: F-4 safety analysis verification and documentation

## Goal
Verify that the AI safety analysis path uses real precomputed safety scores end to end, and update docs so future operators know how to run and validate the batch.

## Files
- `backend-ai/tests/test_safety_analysis.py` - Verify `SAFETY_ANALYSIS` handles populated and missing safety summaries.
- `backend-ai/app/clients/spring_client.py` - Fix any garbled Korean fallback/summary strings found during verification.
- `backend-ai/app/services/analysis_answer_service.py` - Ensure answer generation surfaces score and facility counts clearly.
- `docs/06_EXTERNAL_APIS.md` - Finalize safety source list, formats, env vars, and update cadence.
- `docs/07_DOMAIN_MODEL.md` - Finalize `SafetyFacility` and `PropertyScoreStat` fields if schema changed.
- `docs/08_API_SPEC.md` - Confirm safety API and safety-summary response examples.
- `docs/09_BATCH_INGESTION.md` - Add operational runbook for ingestion and score recalculation.
- `docs/11_ROADMAP.md` - Mark the relevant F-4 safety-score gap as implemented or clarify remaining follow-ups.

## Done When
- [ ] Backend tests pass.
- [ ] Backend AI tests pass.
- [ ] `safety-summary` and `SAFETY_ANALYSIS` are verified against rows produced by the batch/scoring flow.
- [ ] Docs describe how to configure API keys without committing secrets.
- [ ] Docs distinguish MVP point-data safety facilities from excluded WMS-only layers.

## Architecture Rules
- FastAPI may call Spring Boot safety-summary, but Spring Boot must not call an LLM.
- Frontend and user-facing APIs must use stored data, not live public API calls.
- API and domain document changes must stay synchronized with implementation.

## Implementation Instructions
Keep this phase mostly verification and documentation. Only change `backend-ai` behavior if tests reveal a real mismatch or currently garbled user-facing strings. Do not expand into non-MVP news RAG or WMS layer rendering.
