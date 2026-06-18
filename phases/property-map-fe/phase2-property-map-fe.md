# Phase 2: Property Map Frontend

## Goal
Connect the F-1 property search UI to the Spring Boot Property API and show returned properties as Naver Map markers. Keep the scope to map search, marker display, basic filters, and property detail lookup.

## Files
- `frontend/.env.example` - document frontend API and Naver Maps environment variables.
- `frontend/src/api/http.js` - create the shared Axios client for Spring Boot REST calls.
- `frontend/src/api/properties.js` - add Property API request helpers.
- `frontend/src/utils/naverMaps.js` - load the Naver Maps SDK from `VITE_NAVER_MAP_CLIENT_ID`.
- `frontend/src/store/mapStore.js` - replace mock map properties with API-backed state and actions.
- `frontend/src/views/MapExplorer.vue` - render the Naver map, markers, filters, list, and detail panel.

## Done When
- [ ] The frontend requests `GET /api/v1/properties` with current map bounds and active filters.
- [ ] Property markers are rendered on the Naver map and selecting a marker/list item requests `GET /api/v1/properties/{propertyId}`.
- [ ] Basic filters for transaction type, property type, deposit, and sale price are passed to the backend API.
- [ ] Missing map API key and backend API errors show user-readable empty/error states without crashing the page.
- [ ] `pnpm build` succeeds in `frontend`.

## Architecture Rules
- Frontend calls only the Spring Boot REST API.
- API keys and backend URLs are read from environment variables.
- MVP-excluded features such as HUG precise judgment, community, brokerage, and AI registry analysis are not implemented in this phase.
- API response contracts follow `docs/08_API_SPEC.md`.

## Implementation Instructions
Use `VITE_API_BASE_URL` for the Spring Boot base URL and `VITE_NAVER_MAP_CLIENT_ID` for the browser map SDK. Keep the initial map centered around the seeded Seoul property data, then fetch by map viewport after the SDK is ready and whenever the map becomes idle after movement or zoom.
