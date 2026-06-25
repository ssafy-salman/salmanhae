# Phase 3: Public safety data clients and parsers

## Goal
Implement isolated clients/parsers for the four safety data sources without wiring scheduled execution yet. The output of each client must be normalized into the same backend model.

## Files
- `backend/src/main/java/com/ssafy/salmanhae/config/SafetyDataProperties.java` - Add environment-backed configuration for public data keys and source URLs.
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/ingest/SafetyFacilitySourceClient.java` - Define source client contract.
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/ingest/NormalizedSafetyFacility.java` - Define normalized DTO returned by source clients.
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/ingest/CctvCsvClient.java` - Fetch/parse CCTV CSV file data.
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/ingest/EmergencyBellOpenApiClient.java` - Fetch/parse emergency bell OpenAPI data.
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/ingest/SecurityLightOpenApiClient.java` - Fetch/parse security light OpenAPI data.
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/ingest/SafemapPoliceFacilityClient.java` - Fetch/parse Safemap REST XML `IF_0036` police/security facilities.
- `backend/src/test/resources/fixtures/safety/*.xml` - Add small XML fixtures.
- `backend/src/test/resources/fixtures/safety/*.json` - Add small JSON fixtures when the source supports JSON.
- `backend/src/test/resources/fixtures/safety/*.csv` - Add small CSV fixture for CCTV.
- `backend/src/test/java/com/ssafy/salmanhae/service/safety/ingest/*Test.java` - Verify parser behavior with fixtures.
- `docs/06_EXTERNAL_APIS.md` - Note concrete source endpoints and formats if current docs are stale.

## Done When
- [ ] CCTV source is treated as CSV/file data, not paged JSON.
- [ ] Safemap police/security facility source uses REST XML endpoint `https://www.safemap.go.kr/openapi2/IF_0036`.
- [ ] Emergency bell and security light clients support paging according to their public API response metadata.
- [ ] Source clients skip rows without usable coordinates and record enough context for logs.
- [ ] All client parser tests run without network access.

## Architecture Rules
- Public API data must be collected by backend batch and stored in DB; runtime user requests read DB only.
- API keys and secrets must be supplied by environment/configuration, never hardcoded.
- Tests must not depend on live public API availability.

## Implementation Instructions
Separate fetching from parsing so fixture tests can cover parsing without network calls. If a source uses a coordinate system other than WGS84, add a small conversion component and tests before persisting. Keep source identifiers stable: for Safemap `IF_0036`, use `objt_id` as `sourceId` and `IF_0036` as `source`.
