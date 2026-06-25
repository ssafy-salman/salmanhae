# Phase 3: Frontend Map Viewport API

## Goal
Switch the map frontend from loading all properties with `/api/v1/properties` to loading zoom-aware viewport items with `/api/v1/map/viewport`.

## Files
- `frontend/src/api/properties.js` - Add a map viewport API function using current bounds, zoom, and filters
- `frontend/src/api/properties.test.mjs` - Verify the viewport API endpoint and cleaned query params
- `frontend/src/store/mapStore.js` - Store viewport mode, viewport items, loading/error state, and selected property state
- `frontend/src/views/MapExplorer.vue` - Wire map idle/zoom/filter changes to the new API call
- `frontend/package.json` - Run all API tests through `pnpm test`

## Done When
- [x] map movement and zoom call `/api/v1/map/viewport` instead of loading every property.
- [x] requests are debounced or triggered on map idle to avoid excessive network calls.
- [x] property filters are preserved in viewport requests.
- [x] API errors show the existing map error UI without breaking the page.

## Architecture Rules
- Frontend calls Spring Boot REST APIs only.
- State shared between map, list, and chat belongs in Pinia stores.
- UI should keep the existing map/chat layout and not introduce a landing page or unrelated redesign.

## Implementation Instructions
Keep the existing `/api/v1/properties` API available for legacy/detail flows, but make the visible map use the viewport API. Do not call FastAPI from the frontend.
