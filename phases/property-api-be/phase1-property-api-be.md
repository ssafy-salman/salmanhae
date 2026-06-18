# Phase 1: Property API Backend

## Goal
Implement the F-1 public property lookup backend API using the existing `properties` table. The API must support map bounds search, basic filters, and property detail lookup for the frontend map marker flow.

## Files
- `backend/pom.xml` - Add backend dependencies needed for REST API, validation, database access, PostgreSQL runtime, and focused tests.
- `backend/src/main/resources/application.properties` - Add datasource placeholders using environment variables only.
- `backend/src/main/java/com/ssafy/salmanhae/controller/property/*` - Add property REST controller with request validation and delegation only.
- `backend/src/main/java/com/ssafy/salmanhae/service/property/*` - Add property service business logic.
- `backend/src/main/java/com/ssafy/salmanhae/model/dao/property/*` - Add DAO/query layer for `properties`.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/property/*` - Add request/response DTOs for list and detail responses.
- `backend/src/main/java/com/ssafy/salmanhae/common/*` - Add minimal common API response/error handling if no existing pattern exists.
- `backend/src/test/java/com/ssafy/salmanhae/**` - Add tests first for bounds validation, filter handling, list response, detail response, and not-found behavior.
- `docs/08_API_SPEC.md` - Update only if implementation response fields or error behavior differs from the current spec.

## Done When
- [ ] `GET /api/v1/properties?west=...&east=...&south=...&north=...` returns active properties inside the map bounds.
- [ ] The list endpoint supports `transactionType`, `propertyType`, `minDeposit`, `maxDeposit`, `minPrice`, and `maxPrice`.
- [ ] `GET /api/v1/properties/{propertyId}` returns one active property by id.
- [ ] Missing property returns `PROPERTY_NOT_FOUND` with HTTP 404.
- [ ] Invalid bounds return `INVALID_BOUNDS` or `INVALID_REQUEST` with HTTP 400.
- [ ] Responses use camelCase JSON and the common `{ data, message }` success envelope from `docs/08_API_SPEC.md`.
- [ ] Business logic lives in Service classes; Controller only validates input and delegates.
- [ ] `cd backend && ./mvnw test` passes.

## Architecture Rules
- F-1 is public: property lookup must not require Supabase JWT.
- Frontend will call only Spring Boot REST APIs.
- Public API data must be read from DB, not live external API calls.
- All business logic must live in Service classes.
- API keys, DB URLs, usernames, and passwords must be read from environment variables only.
- Do not implement MVP-excluded features: real brokerage, community, precise HUG judgment, registry AI analysis.
- Do not implement F-4/F-3 scope in this phase: safety summary, region price average layer, and transaction comparison endpoints are follow-up phases.

## Implementation Instructions
1. Start with backend tests that describe the expected controller/service behavior.
2. Prefer the repository's documented Controller-Service-DAO layering. If adding a persistence dependency, keep it minimal and aligned with the existing architecture documentation.
3. Use `properties.latitude` and `properties.longitude` for bounds filtering and `is_active = true` for visible map properties.
4. Keep query filters optional and composable. Numeric filters should ignore null values.
5. Return only fields already documented for the F-1 property list/detail API unless the spec is updated in the same phase.
6. Do not call Naver Maps, MOLIT, Supabase REST, FastAPI, or any LLM from this backend API.
7. Run `cd backend && ./mvnw test` before completing the phase.
