# Phase 3: Legal RAG Retriever

## Goal
Replace the legal RAG stub with a testable backend-ai retriever boundary that prepares query embeddings, performs pgvector similarity search, and returns normalized legal cards. This phase keeps the implementation offline-testable by injecting fake embedding and vector clients in tests.

## Files
- `backend-ai/tests/test_legal_retriever.py` - tests for legal retriever normalization, empty queries, and pgvector client delegation
- `backend-ai/app/rag/retriever.py` - legal RAG retrieval service with dependency injection
- `backend-ai/app/clients/supabase_client.py` - pgvector SQL client boundary for legal document chunks
- `backend-ai/app/clients/embedding_client.py` - embedding client boundary driven by environment configuration
- `backend-ai/app/graph/nodes/legal_rag.py` - legal_rag node using the retriever boundary

## Done When
- [ ] Legal retriever tests pass without network or database access
- [ ] Stubbed legal cards are removed from production client code
- [ ] Retriever validates blank queries and clamps top_k to a safe range
- [ ] Supabase pgvector search maps rows to legal card fields expected by the chat contract
- [ ] `legal_rag` node records tool metadata without Spring or frontend direct pgvector access

## Architecture Rules
- pgvector similarity search belongs only in FastAPI `backend-ai`.
- Spring Boot must not call LLMs or pgvector directly.
- API keys and database URLs must be read from environment settings only.
- F-3 MVP legal RAG is limited to official legal document chunks; news RAG and registry AI are out of scope.

## Implementation Instructions
Write tests first. Keep the retriever injectable so tests can use fake embedding and vector clients. Do not require live Supabase or OpenAI calls in unit tests. Production code may define the SQL and client boundary, but it must not hardcode secrets or fallback to fake legal content.
