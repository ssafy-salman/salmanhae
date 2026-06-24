# Phase 5: Property safety score calculation batch

## Goal
Calculate per-property safety counts and weighted safety scores from stored `safety_facility` rows, then upsert them into `property_score_stat`.

## Files
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/PropertySafetyScoreService.java` - Define score recalculation use case.
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/PropertySafetyScoreServiceImpl.java` - Calculate counts, normalize metrics, and upsert scores.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/safety/PropertySafetyScoreInput.java` - Represent counts used by the pure scorer if useful.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/safety/PropertySafetyScoreResult.java` - Represent calculated score and counts.
- `backend/src/main/java/com/ssafy/salmanhae/batch/PropertySafetyScoreScheduler.java` - Trigger score recalculation after safety facility refresh.
- `backend/src/main/java/com/ssafy/salmanhae/model/dao/property/PropertyDao.java` - Add methods needed to list active properties and upsert score stats.
- `backend/src/main/java/com/ssafy/salmanhae/model/dao/property/JdbcPropertyDao.java` - Implement active property listing and `property_score_stat` upsert.
- `backend/src/test/java/com/ssafy/salmanhae/service/safety/PropertySafetyScoreServiceTest.java` - Verify scoring formula and count aggregation.
- `backend/src/test/java/com/ssafy/salmanhae/controller/property/PropertyControllerTest.java` - Verify `safety-summary` reflects calculated DB values.
- `docs/09_BATCH_INGESTION.md` - Document the final scoring formula and recalculation timing.

## Done When
- [ ] Counts are calculated with CCTV, emergency bell, and security light within 300m and police/security facilities within 500m.
- [ ] Safety score uses documented weights: CCTV 30%, emergency bell 25%, security light 25%, police 20%.
- [ ] Score calculation is deterministic and covered by pure unit tests.
- [ ] `property_score_stat` upsert preserves or intentionally recalculates `price_score` according to the chosen policy.
- [ ] `GET /api/v1/properties/{id}/safety-summary` returns the recalculated score and counts.

## Architecture Rules
- Safety score calculation must be precomputed by batch into `property_score_stat`.
- Public API calls must not happen during user API requests.
- Controllers should not contain score calculation logic.

## Implementation Instructions
Avoid introducing a PostGIS dependency unless already enabled. A bounding-box prefilter plus Haversine distance calculation is acceptable for MVP. Make the normalization policy explicit in code and docs; if there is no facility data for a metric, score that metric as 0 rather than inventing data.
