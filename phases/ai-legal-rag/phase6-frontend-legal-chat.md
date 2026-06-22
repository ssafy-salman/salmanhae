# Phase 6: Frontend Legal Chat

## Goal
Connect the Vue chatbot screen to the Spring Boot `/api/v1/chat` endpoint so F-3 legal RAG answers and legal reference cards are visible to authenticated users.

## Files
- `frontend/src/api/chat.js` - add the chat API client and response normalization
- `frontend/src/api/chat.test.mjs` - add offline tests for chat response normalization
- `frontend/src/api/http.js` - attach JWT authorization from local storage when available
- `frontend/src/store/mapStore.js` - add chat state, loading/error handling, and API-backed send action
- `frontend/src/views/Chatbot.vue` - render API-backed chat messages, legal cards, loading, and error states
- `frontend/package.json` - add a frontend test script
- `phases/ai-legal-rag/phase6-frontend-legal-chat.md` - phase specification

## Done When
- [ ] Chat requests call only Spring Boot `/api/v1/chat`, never FastAPI directly
- [ ] Legal RAG responses render answer text and legal cards with law/article/title/content/score
- [ ] Loading and error states are visible without breaking the conversation history
- [ ] Auth token is sent through the existing Axios client when present
- [ ] Frontend tests and build pass

## Architecture Rules
- Frontend calls Spring Boot REST APIs only.
- F-3 is an authenticated feature; chat requests include `Authorization: Bearer {jwt}` when a token exists.
- Business logic remains in backend services; frontend only renders API responses and UI state.
- MVP scope excludes community, registry AI analysis, and HUG precise judgment.

## Implementation Instructions
Write tests first around a pure chat response normalizer. Keep the UI consistent with the existing app rather than creating a landing page. Preserve current quick-question workflow, but replace mock bot replies with the real Spring chat response and legal card rendering.
