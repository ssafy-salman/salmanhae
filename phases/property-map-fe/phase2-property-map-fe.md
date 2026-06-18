# Phase 2: Property Map Frontend

## Goal
Connect the F-1 property search UI to the Spring Boot Property API and show returned properties as Naver Map markers. Keep the scope to map search, marker display, basic filters, and property detail lookup.

## Files
- `frontend/.env.example` - document frontend API and Naver Maps environment variables.
- `frontend/pnpm-workspace.yaml` - correct the frontend pnpm workspace settings so local install/build commands work.
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
Use `VITE_API_BASE_URL` for the Spring Boot base URL and `VITE_NAVER_MAP_CLIENT_ID` for the browser map SDK. Initialize the map with a fixed Seoul viewport centered at latitude `37.5665`, longitude `126.9780`, zoom `12`, and fallback bounds `west=126.76`, `east=127.18`, `south=37.42`, `north=37.66`. Fetch properties by the current map bounds after the SDK is ready and whenever the map becomes idle after movement or zoom. If the backend returns no properties, keep this fixed viewport and show the empty state rather than auto-fitting or panning to another region.
