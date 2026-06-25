# Phase 3: Offline Data Pipeline

## Goal
Build an offline MVP data pipeline that collects MOLIT real transaction data, computes price statistics, generates synthetic F-1 property rows from real building anchors, and upserts the result into Supabase without committing generated data artifacts.

## Files
- `scripts/data_pipeline/pipeline.py` - collect XML responses, normalize transactions, geocode building anchors, generate properties, and load Supabase tables.
- `scripts/data_pipeline/README.md` - document environment variables, execution commands, and generated artifact lifecycle.
- `scripts/data_pipeline/requirements.txt` - list optional DB loader dependency.
- `data/reference/lawd-codes.example.csv` - provide a small local planning/test fixture.
- `database/migrations/202606230001_create_price_stats.sql` - add region/building price statistic tables.
- `database/README.md` - document migration order and data loading policy.
- `docs/06_EXTERNAL_APIS.md` - document external API usage and persisted datasets.
- `docs/07_DOMAIN_MODEL.md` - document transaction/stat/property data model decisions.
- `docs/09_BATCH_INGESTION.md` - document the MVP offline ingestion policy.
- `.gitignore` - keep generated raw, normalized, and SQL seed artifacts out of git.

## Done When
- [x] `python -m py_compile scripts/data_pipeline/pipeline.py` passes.
- [x] `python scripts/data_pipeline/pipeline.py plan --lawd-codes data/reference/lawd-codes.example.csv --months 2 --limit-regions 2 --source-apis MOLIT_APT_RENT` shows a valid request plan.
- [x] A small live run can fetch, normalize, geocode, and generate property rows without DB loading.
- [x] Generated data directories are ignored or removed from tracked changes.
- [x] Domain, external API, and batch ingestion docs describe the offline data pipeline and artifact lifecycle.

## Architecture Rules
- Public API data is collected and stored before client requests; runtime map APIs read from DB only.
- Secrets are loaded from environment files or deployment environment variables and are never hardcoded.
- Data model changes must update `docs/07_DOMAIN_MODEL.md`.

## Implementation Instructions
Use recent 12 months nationwide MOLIT transaction APIs for apartment, officetel, villa/row-house, and multi-family sale/rent data. Generate 1-2 `MVP_SYNTHETIC` properties per geocoded building anchor. If geocoding fails, keep the transaction rows and skip only the property rows. Upsert into Supabase and do not truncate existing data.
