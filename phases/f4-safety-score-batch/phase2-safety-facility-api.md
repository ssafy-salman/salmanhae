# Phase 2: Safety facility query API

## Goal
Expose stored safety facilities through Spring Boot so the frontend can render safety overlays without calling public APIs directly.

## Files
- `backend/src/main/java/com/ssafy/salmanhae/controller/safety/SafetyFacilityController.java` - Add `GET /api/v1/safety/facilities`.
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/SafetyFacilityService.java` - Define bounds query use case.
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/SafetyFacilityServiceImpl.java` - Validate inputs and delegate to DAO.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/safety/SafetyFacilityQueryRequest.java` - Represent validated query parameters if useful.
- `backend/src/test/java/com/ssafy/salmanhae/controller/safety/SafetyFacilityControllerTest.java` - Cover valid query, type filtering, and invalid bounds.
- `docs/08_API_SPEC.md` - Adjust the Safety API section if implementation fields differ from the current spec.

## Done When
- [ ] `GET /api/v1/safety/facilities?types=CCTV,EMERGENCY_BELL&west=...&east=...&south=...&north=...` returns `items` and `totalCount`.
- [ ] Invalid bounds return the existing `INVALID_BOUNDS` or `INVALID_REQUEST` error style.
- [ ] Unknown `types` values return `INVALID_REQUEST`.
- [ ] Endpoint remains public according to existing Spring Security rules.
- [ ] Backend tests pass for API and Service validation.

## Architecture Rules
- Frontend must call only Spring Boot REST APIs.
- Controllers perform input validation and delegation only; business logic belongs in Service classes.
- API response format changes must be reflected in `docs/08_API_SPEC.md`.

## Implementation Instructions
Prefer the repository's existing `ApiResponse` and `ListResponse` conventions. Reuse or mirror map bounds validation patterns from the map/property APIs so coordinate handling stays consistent.
