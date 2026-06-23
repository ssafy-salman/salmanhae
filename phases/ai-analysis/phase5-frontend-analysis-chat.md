# Phase 5: Frontend Analysis Chat

## Goal
Expose F-4 analysis in the Vue chatbot by sending selected property context and rendering analysis cards.

## Files
- `frontend/src/api/chat.test.mjs` - add tests for selected property request payload and analysis card normalization.
- `frontend/src/api/chat.js` - include selectedPropertyId in chat requests.
- `frontend/src/api/chat-normalizer.js` - normalize analysis cards.
- `frontend/src/store/mapStore.js` - pass selected property context and store analysis cards on messages.
- `frontend/src/views/Chatbot.vue` - render compact price/safety analysis cards.
- `docs/08_API_SPEC.md` - adjust frontend-visible examples if needed.

## Done When
- [ ] Chat requests include selected property ID when a map property is selected.
- [ ] Price and safety analysis cards render in the chat flow.
- [ ] Legal cards and recommendation properties remain backward compatible.
- [ ] Frontend tests pass.

## Architecture Rules
- Frontend calls only Spring Boot `/api/v1/chat`.
- Main service UI remains map + chatbot focused.
- Do not build MVP-excluded features or a new landing page.

## Implementation Instructions
Keep the UI compact and consistent with the existing Chatbot view. Add tests around pure normalization before wiring the store and component.
