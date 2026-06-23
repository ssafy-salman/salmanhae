# Phase 4: Grounded Analysis Answer

## Goal
Generate user-facing F-4 analysis answers from tool results while keeping deterministic behavior in tests.

## Files
- `backend-ai/tests/test_agent_chat.py` - assert price and safety answers cite tool-derived facts.
- `backend-ai/tests/test_analysis_answer_generation.py` - cover deterministic answer generation from analysis cards.
- `backend-ai/app/clients/llm_client.py` - include analysis cards/tool results in answer generation context.
- `backend-ai/app/rag/prompts.py` - add concise F-4 answer guidance if needed.
- `backend-ai/app/graph/nodes/generate_answer.py` - preserve current graph boundary.

## Done When
- [ ] Price analysis answer mentions concrete comparable transaction or price-stat facts.
- [ ] Safety analysis answer mentions concrete score/count facts.
- [ ] Answers avoid HUG eligibility conclusions and legal advice beyond MVP scope.
- [ ] backend-ai tests pass with deterministic fallback.

## Architecture Rules
- Spring Boot must not call an LLM directly.
- LLM prompts must use tool results as grounding context.
- MVP scope excludes HUG, news RAG, WMS, and registry-document AI.

## Implementation Instructions
Write tests first around deterministic fallback output. Live LLM behavior may remain optional through existing environment configuration.
