# Phase 2: Spring Analysis APIs

## Goal
Implement the public Spring Boot analysis endpoints that F-4 tools will later call. These endpoints read cached database data only and return transaction comparison and safety summary data.

## Files
- `backend/src/test/java/com/ssafy/salmanhae/controller/property/PropertyControllerTest.java` - add tests for transactions and safety summary endpoints.
- `backend/src/test/java/com/ssafy/salmanhae/controller/price/PriceAnalysisControllerTest.java` - add tests for regional price analysis.
- `backend/src/test/resources/schema.sql` - add test tables for transaction history, building price stats, and property score stats.
- `backend/src/test/resources/data.sql` - seed deterministic F-4 analysis data.
- `backend/src/main/java/com/ssafy/salmanhae/controller/property/PropertyController.java` - expose property transaction and safety summary endpoints.
- `backend/src/main/java/com/ssafy/salmanhae/controller/price/PriceAnalysisController.java` - expose region price analysis endpoint.
- `backend/src/main/java/com/ssafy/salmanhae/service/property/*` - keep analysis orchestration in services.
- `backend/src/main/java/com/ssafy/salmanhae/model/dao/property/*` - add cached-data queries.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/property/*` - add response DTOs.
- `docs/08_API_SPEC.md` - update endpoint response details if the shape differs from the current draft.

## Done When
- [ ] `GET /api/v1/properties/{id}/transactions` returns recent comparable transactions.
- [ ] `GET /api/v1/properties/{id}/safety-summary` returns precomputed property score stats.
- [ ] `GET /api/v1/price-analysis` returns region/building cached price statistics.
- [ ] Missing properties return `PROPERTY_NOT_FOUND`.
- [ ] Backend tests pass.

## Architecture Rules
- Runtime requests must query DB only; do not call public external APIs.
- Safety scores must be read from `property_score_stat`, not calculated per request.
- Business logic lives in Service classes.

## Implementation Instructions
Start from tests. Prefer small DTO records and DAO methods that match the existing JDBC pattern. Do not add schema beyond cached F-4 data needed by the tests.
