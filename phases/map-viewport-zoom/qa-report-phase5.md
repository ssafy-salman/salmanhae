# Phase 5 QA Report

## Scope

- Issue: #61
- Date: 2026-06-24
- Target: zoom-aware map viewport flow for F-1 property search

## Contract Check

- `GET /api/v1/map/viewport` remains the frontend map data source.
- Zoom thresholds remain unchanged:
  - `<= 11`: `SIGUNGU_AVG`
  - `12`-`13`: `DONG_AVG`
  - `14`-`15`: `PROPERTY_CLUSTER`
  - `>= 16`: `PROPERTY_MARKER`
- `SIGUNGU_AVG` now aggregates active visible properties directly by `sigungu` so broad zoom requests stay small and do not depend on the heavier precomputed region-stat join.

## Deployment Probe Before Fix

Checked the deployed Cloud Run API at:

`https://salmanhae-api-370583013156.asia-northeast3.run.app/api/v1/map/viewport`

Using Seoul-wide bounds:

| zoom | observed status | observed mode |
| --- | ---: | --- |
| 9 | 401 | none |
| 10 | 401 | none |
| 11 | 401 | none |
| 12 | 200 | `DONG_AVG` |
| 14 | 200 | `PROPERTY_CLUSTER` |
| 16 | 200 | `PROPERTY_MARKER` |

The failure was limited to the broad `SIGUNGU_AVG` branch. `PROPERTY_CLUSTER` returned 360 cluster items and `PROPERTY_MARKER` returned the existing 500 item cap, so the remaining risk was the broad-region query path.

## Local Verification

Commands run:

```bash
cd backend && ./mvnw.cmd -Dtest=MapViewportControllerTest test
cd backend && ./mvnw.cmd test
cd frontend && CI=true pnpm test
cd frontend && CI=true pnpm build
python scripts/execute_codex.py map-viewport-zoom --dry-run
```

Expected after merge:

- Backend GitHub Actions deploys `salmanhae-api` on `develop` pushes that touch `backend/**`.
- Vercel deploys the frontend from the existing frontend project integration on `develop`.
- No new secrets or Cloud Run service changes are required.
