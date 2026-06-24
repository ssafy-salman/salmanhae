# Phase 4: Safety facility ingestion batch

## Goal
Wire the safety source clients into a Spring batch/scheduler service that upserts normalized safety facilities into `safety_facility`.

## Files
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/SafetyFacilityIngestionService.java` - Define ingestion use case.
- `backend/src/main/java/com/ssafy/salmanhae/service/safety/SafetyFacilityIngestionServiceImpl.java` - Run source clients, normalize, validate, and upsert.
- `backend/src/main/java/com/ssafy/salmanhae/batch/SafetyFacilityIngestionScheduler.java` - Add scheduled monthly ingestion entrypoint.
- `backend/src/main/java/com/ssafy/salmanhae/model/dto/safety/SafetyFacilityIngestionResult.java` - Return per-source counts and failures.
- `backend/src/test/java/com/ssafy/salmanhae/service/safety/SafetyFacilityIngestionServiceTest.java` - Verify partial failure behavior and upsert calls.
- `backend/src/test/java/com/ssafy/salmanhae/batch/SafetyFacilityIngestionSchedulerTest.java` - Verify scheduler delegates to service when enabled.
- `docs/09_BATCH_INGESTION.md` - Document monthly safety ingestion command/schedule and retry behavior.

## Done When
- [ ] Batch can be disabled in local/test profiles by configuration.
- [ ] One failing source does not prevent other sources from being processed.
- [ ] Per-source inserted/updated/skipped/failed counts are logged or returned.
- [ ] Re-running ingestion is idempotent because DAO upsert handles duplicates.
- [ ] Backend tests pass without real network calls.

## Architecture Rules
- Business logic belongs in Service classes; scheduler only triggers and logs.
- Public data should be accumulated/upserted, not blindly truncated.
- Runtime client requests must not call public APIs.

## Implementation Instructions
Use dependency injection for source clients so tests can provide fake clients. Prefer a single transaction per source or per chunk rather than one giant transaction for all sources. Keep manual run support in the Service so later admin/CLI triggers can reuse it.
