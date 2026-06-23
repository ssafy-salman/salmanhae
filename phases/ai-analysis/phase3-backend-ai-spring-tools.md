# Phase 3: Backend-AI Spring Tools

## Goal
Replace F-4 backend-ai stubs with real internal Spring Boot tool calls for price and safety analysis.

## Files
- `backend-ai/tests/test_agent_chat.py` - add integration-style tests with mocked Spring tool responses.
- `backend-ai/tests/test_spring_client.py` - add unit tests for SpringClient HTTP request mapping and failures.
- `backend-ai/app/clients/spring_client.py` - call Spring Boot analysis endpoints with timeouts and safe error payloads.
- `backend-ai/app/graph/nodes/price_analysis.py` - map Spring price analysis data into analysis cards.
- `backend-ai/app/graph/nodes/safety_analysis.py` - map Spring safety summary data into analysis cards.
- `backend-ai/app/core/config.py` - add any needed Spring client timeout settings.

## Done When
- [ ] `analyze_price` calls Spring Boot with selected property context.
- [ ] `analyze_safety` calls Spring Boot with selected property context.
- [ ] Tool failures produce a controlled F-4 fallback instead of an unhandled exception.
- [ ] backend-ai tests pass without live Spring Boot.

## Architecture Rules
- Frontend never calls backend-ai directly.
- backend-ai calls Spring Boot over internal HTTP for property, price, and safety data.
- No pgvector or news RAG is introduced for F-4 MVP.

## Implementation Instructions
Use mocked HTTP clients in tests. Keep the production client free of hardcoded API keys or URLs; read base URL and timeouts from configuration.
