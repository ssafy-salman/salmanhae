# Phase 1: Safety facility schema and domain base

## Goal
Create the database and backend domain foundation for storing safety facilities collected from public APIs. This phase should not call external APIs yet; it only prepares schema, DTOs, enums, DAO contracts, and tests.

## Files
- `database/migrations/202606240001_create_safety_facility.sql` - Create `safety_facility` table, indexes, and source de-duplication constraints.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/safety/SafetyFacilityType.java` - Add `CCTV`, `EMERGENCY_BELL`, `SECURITY_LIGHT`, `POLICE` enum.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/safety/SafetyFacilityRow.java` - Add row model for DAO reads and writes.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/safety/SafetyFacilityResponse.java` - Add public response DTO for map overlays.
- `backend/src/main/java/com/ssafy/salmanhae/model/dao/safety/SafetyFacilityDao.java` - Define query and upsert contracts.
- `backend/src/main/java/com/ssafy/salmanhae/model/dao/safety/JdbcSafetyFacilityDao.java` - Implement typed DAO methods using `NamedParameterJdbcTemplate`.
- `backend/src/test/resources/schema.sql` - Mirror the test schema for `safety_facility`.
- `backend/src/test/resources/data.sql` - Add small deterministic fixture rows for all safety facility types.
- `backend/src/test/java/com/ssafy/salmanhae/model/dao/safety/JdbcSafetyFacilityDaoTest.java` - Verify inserts/upserts and bounds queries.

## Done When
- [ ] `safety_facility` has fields compatible with `docs/07_DOMAIN_MODEL.md`: `id`, `type`, `name`, `address`, `latitude`, `longitude`, `source`, `source_id`, `description`, `updated_at`.
- [ ] Duplicate public data is prevented by a unique key on `type`, `source`, and `source_id`.
- [ ] DAO tests prove that repeated upserts update existing rows instead of creating duplicates.
- [ ] Invalid or missing coordinates are not persisted by DAO upsert methods.

## Architecture Rules
- All business rules must stay in Service classes; DAO should only persist/query data.
- Public API keys and secrets must not be hardcoded.
- Data model changes must update `docs/07_DOMAIN_MODEL.md` in a later documentation phase if implementation details differ from current docs.

## Implementation Instructions
Start with tests for DAO behavior and schema expectations. Use plain latitude/longitude columns and normal PostgreSQL indexes; do not require PostGIS unless the repository already enables it. Keep the schema compatible with Supabase PostgreSQL and the current `database/migrations` style.
