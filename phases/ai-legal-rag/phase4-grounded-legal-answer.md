# Phase 4: Grounded Legal Answer

## Goal
Use retrieved legal cards as grounded context when generating F-3 legal consultation answers. This phase makes the answer text cite the retrieved law/article titles and provide a clear non-legal-advice caution without changing the public chat response schema.

## Files
- `backend-ai/tests/test_legal_answer_generation.py` - tests for legal prompt construction and grounded answer behavior
- `backend-ai/app/rag/prompts.py` - legal RAG prompt/context formatting helpers
- `backend-ai/app/clients/llm_client.py` - legal consultation answer generation using retrieved cards
- `backend-ai/tests/test_agent_chat.py` - chat integration assertion for grounded legal answer text

## Done When
- [ ] Legal answers include retrieved law name, article number/title, and a short explanation
- [ ] Legal answers include a contract review/professional consultation caution
- [ ] No legal answer invents a citation when no legal cards were retrieved
- [ ] Tests pass without live LLM, network, or database access
- [ ] Response shape remains compatible with the existing Spring chat contract

## Architecture Rules
- AI answer generation stays in `backend-ai`; Spring Boot remains an internal HTTP proxy.
- pgvector retrieval remains in `backend-ai` only.
- API keys and secrets must come from environment settings only.
- F-3 MVP is limited to housing lease legal RAG; news RAG, HUG precision judgment, and registry AI remain out of scope.

## Implementation Instructions
Write tests first. Keep the implementation deterministic for unit tests while preserving a clear prompt/context boundary for a future live LLM call. Do not change the `/internal/agent/chat` response schema.
