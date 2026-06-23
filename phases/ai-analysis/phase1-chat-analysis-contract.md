# Phase 1: Chat Analysis Contract

## Goal
Lock the F-4 chat contract before adding deeper analysis tools. The Spring chat endpoint must pass selected property context to backend-ai and return structured analysis cards for price and safety analysis intents.

## Files
- `backend/src/test/java/com/ssafy/salmanhae/controller/chat/ChatControllerTest.java` - add authenticated contract coverage for F-4 analysis responses.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/chat/ChatRequest.java` - accept optional selected property context.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/chat/ChatResponse.java` - expose analysis cards in the public chat response.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/chat/AnalysisCardResponse.java` - add the structured F-4 analysis card DTO.
- `backend/src/main/java/com/ssafy/salmanhae/service/chat/AiAgentClient.java` - forward selected property context and map analysis cards from backend-ai.
- `backend-ai/tests/test_agent_chat.py` - assert backend-ai returns selected-property analysis tool results in camelCase.
- `backend-ai/app/api/schemas.py` - expose analysis cards in the internal response schema.
- `backend-ai/app/graph/state.py` - carry analysis cards through LangGraph state.
- `backend-ai/app/graph/nodes/price_analysis.py` - emit deterministic price analysis card from current stub data.
- `backend-ai/app/graph/nodes/safety_analysis.py` - emit deterministic safety analysis card from current stub data.
- `docs/08_API_SPEC.md` - document selected property context and analysis card response shape.

## Done When
- [ ] Spring `POST /api/v1/chat` accepts `selectedPropertyId` and returns `analysisCards`.
- [ ] Spring forwards `selectedPropertyId` to backend-ai as `context.selectedPropertyId`.
- [ ] backend-ai price and safety analysis responses include deterministic `analysisCards`.
- [ ] API spec documents the F-4 chat contract.
- [ ] Backend and backend-ai contract tests pass.

## Architecture Rules
- All Spring business logic remains in service/client boundaries; the controller only validates and delegates.
- Frontend must call Spring Boot only; FastAPI remains internal.
- F-2~F-8 AI agent calls stay behind Spring Security JWT validation.
- Do not implement HUG, news RAG, WMS layers, or direct runtime public API calls.

## Implementation Instructions
Write failing tests first for the selected property context and analysis card contract. Keep Phase 1 deterministic by using current backend-ai stub data; real Spring analysis API calls belong to later phases.
