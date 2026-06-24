# Phase 2: Region And Cluster Query

## Goal
Populate `/api/v1/map/viewport` with real region-average and cluster data from PostgreSQL without sending thousands of properties to the client.

## Files
- `backend/src/test/java/com/ssafy/salmanhae/service/map/MapViewportServiceTest.java` - Service tests for mode-specific query behavior
- `backend/src/main/java/com/ssafy/salmanhae/model/dao/property/PropertyDao.java` - DAO methods for region averages, property clusters, and detailed markers
- `backend/src/main/java/com/ssafy/salmanhae/model/dao/property/JdbcPropertyDao.java` - SQL implementations using bounds and filters
- `backend/src/main/java/com/ssafy/salmanhae/service/map/MapViewportServiceImpl.java` - Compose mode-specific items and enforce maximum payload sizes
- `backend/src/test/resources/schema.sql` - Test schema adjustments only if needed
- `backend/src/test/resources/data.sql` - Test fixtures for region and cluster data

## Done When
- [ ] region modes return `REGION_AVG` items with region labels, average prices, transaction counts, and usable marker coordinates.
- [ ] zoom `14`-`15` returns `CLUSTER` items grouped by a deterministic coordinate grid.
- [ ] zoom `16+` returns individual `PROPERTY` items, with clustering or a cap applied if the bounds are still too dense.
- [ ] Existing `/api/v1/properties` behavior is unchanged.

## Architecture Rules
- Public API requests must query stored DB data only; no external public API call is made on request path.
- Query and aggregation logic stays behind DAO and Service boundaries.
- Avoid schema changes unless the existing `region_price_stat` data cannot produce reliable coordinates.

## Implementation Instructions
Prefer deriving region marker coordinates from active `properties` grouped by `sido/sigungu/dong` so this phase can avoid a production migration. If that proves unreliable, stop and document the required `region_price_stat` coordinate migration before implementing it.
