# Phase 1: Map Viewport API Contract

## Goal
Define the backend contract for zoom-aware map data so the frontend can stop loading every property in the current bounds. Add tests first for `/api/v1/map/viewport` mode selection, response shape, validation, and public access.

## Files
- `backend/src/test/java/com/ssafy/salmanhae/controller/map/MapViewportControllerTest.java` - MockMvc contract tests for the new endpoint
- `backend/src/main/java/com/ssafy/salmanhae/controller/map/MapViewportController.java` - Controller that validates request params and delegates to service
- `backend/src/main/java/com/ssafy/salmanhae/service/map/MapViewportService.java` - Service boundary for zoom-aware map data
- `backend/src/main/java/com/ssafy/salmanhae/service/map/MapViewportServiceImpl.java` - Minimal implementation of zoom threshold routing
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/map/*.java` - DTOs/enums for map viewport request and response items
- `docs/08_API_SPEC.md` - Document the cluster-specific viewport mode and zoom threshold policy

## Done When
- [ ] `GET /api/v1/map/viewport` is publicly accessible without JWT.
- [ ] zoom `11` returns `SIGUNGU_AVG`, zoom `12`-`13` returns `DONG_AVG`, zoom `14`-`15` returns `PROPERTY_CLUSTER`, and zoom `16+` returns `PROPERTY_MARKER`.
- [ ] invalid bounds or missing zoom returns `400 INVALID_REQUEST` or the existing bounds validation error.
- [ ] Backend tests for the controller contract pass.
- [ ] API spec describes the implemented threshold policy.

## Architecture Rules
- Business logic belongs in Service classes; the Controller only validates input and delegates.
- API response shape must match `docs/08_API_SPEC.md` camelCase JSON.
- F-1 is public; it must not require Spring Security JWT.

## Implementation Instructions
Start with failing MockMvc tests for the endpoint. Implement only enough backend structure to route by zoom and return the documented response envelope, using empty `items` for phase1 if DAO queries are not ready yet.
