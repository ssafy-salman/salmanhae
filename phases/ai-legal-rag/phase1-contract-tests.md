# Phase 1: F-3 Contract and Tests

## Goal
Define the first user-visible F-3 chat contract and lock it with tests before deeper RAG ingestion work. Keep the implementation minimal but runnable so later phases can replace stubs with real pgvector and LLM behavior.

## Files
- `backend/src/test/java/com/ssafy/salmanhae/controller/chat/ChatControllerTest.java` - Spring chat API authentication and response contract tests
- `backend/src/main/java/com/ssafy/salmanhae/controller/chat/ChatController.java` - authenticated `/api/v1/chat` endpoint
- `backend/src/main/java/com/ssafy/salmanhae/service/chat/ChatService.java` - service boundary for AI agent delegation
- `backend/src/main/java/com/ssafy/salmanhae/service/chat/ChatServiceImpl.java` - minimal AI agent delegation implementation
- `backend/src/main/java/com/ssafy/salmanhae/service/chat/AiAgentClient.java` - internal FastAPI client boundary
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/chat/*.java` - request/response DTOs
- `backend-ai/tests/test_agent_chat.py` - backend-ai legal RAG response contract tests

## Done When
- [ ] `POST /api/v1/chat` rejects unauthenticated requests with `401`
- [ ] authenticated legal questions return `intent = LEGAL_CONSULT`, a message, and non-empty `legalCards`
- [ ] backend-ai `/internal/agent/chat` returns legal cards using the public camelCase contract
- [ ] Targeted backend and backend-ai tests pass

## Architecture Rules
- F-3 requires authentication and must pass through Spring Security JWT verification.
- Frontend must call Spring Boot only; Spring Boot delegates to FastAPI over internal HTTP.
- Business logic belongs in Service classes; Controller validates and delegates.
- LangGraph and RAG logic stay in `backend-ai`.
- API keys and internal secrets are injected from configuration or environment variables.

## Implementation Instructions
Start with tests, then add the smallest Spring chat endpoint and service/client boundary needed for a passing contract. Do not implement legal document ingestion, pgvector schema, or real LLM calls in this phase; those belong to later phases.
