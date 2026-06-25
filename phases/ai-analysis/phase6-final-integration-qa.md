# Phase 6: Final Integration QA

## Goal
Close F-4 by validating the end-to-end analysis flow across Spring Boot, backend-ai, frontend, and documentation. Keep the scope to MVP price/safety analysis only.

## Verification Scope
- `frontend/src/api/chat.test.mjs` already covers `selectedPropertyId` request payload handling and normalization of PRICE/SAFETY `analysisCards`.
- `backend-ai/tests/test_agent_chat.py` already verifies PRICE/SAFETY routing, tool result grounding, and `analysisCards[].metrics.selectedPropertyId` propagation.
- `backend/src/test/java/com/ssafy/salmanhae/controller/chat/ChatControllerTest.java` now covers authenticated `/api/v1/chat` PRICE and SAFETY analysis card contracts.
- `docs/08_API_SPEC.md` now documents frontend-visible PRICE/SAFETY `analysisCards` examples and standard metric keys.
- `phases/ai-analysis/phase6-final-integration-qa.md` records the final F-4 QA scope and completion criteria.

## Completed Criteria
- [x] `selectedPropertyId` is covered from frontend request payload through backend-ai analysis cards and Spring `/api/v1/chat` response.
- [x] PRICE and SAFETY cards include `selectedPropertyId` in metrics where the selected property context is present.
- [x] Safety analysis test assertions cover the documented `radius`, `safetyScore`, `cctvCount300m`, `bellCount300m`, `lightCount300m`, and `policeCount500m` metric keys.
- [x] Price/safety analysis remains grounded in tool results and excludes MVP-out-of-scope HUG/legal conclusions.
- [x] Frontend-visible API spec matches the implemented request and analysis card response shape.
- [x] Relevant backend, backend-ai, and frontend tests pass or any environment limitation is documented.

## Architecture Rules
- Frontend calls only Spring Boot `/api/v1/chat`.
- Spring Boot does not call an LLM directly.
- FastAPI owns LangGraph intent routing and LLM answer generation.
- MVP scope excludes HUG precision checks, news RAG, WMS layers, and registry-document AI.

## Final Deliverables
- Ensure all PRICE and SAFETY analysis-card tests include `selectedPropertyId` in metrics when selected property context is present.
- Verify `docs/08_API_SPEC.md` examples match the response structure covered by `backend-ai/tests/test_agent_chat.py` and `ChatControllerTest`.
- Keep phase6 limited to regression coverage and documentation alignment; do not add new user-facing flows.
