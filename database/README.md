# Database

This directory stores reproducible schema migrations for the shared Supabase
PostgreSQL database.

## Apply Order

Run migrations in numeric order:

1. `migrations/202606160001_create_properties.sql`
2. `migrations/202606220001_create_legal_document_chunks.sql`
3. `migrations/202606230001_create_price_stats.sql`
4. `migrations/202606230002_cleanup_region_price_stat_codes.sql`
5. `migrations/202606230003_create_property_score_stat.sql`

## Data Loading Policy

Do not commit generated nationwide transaction/property seed SQL files.

F-1 and price-stat data are now loaded by the offline data pipeline:

```bash
python scripts/data_pipeline/pipeline.py run --months 12 --scope nationwide --migrate-db --load-db
```

The pipeline upserts into:

- `transaction_history`
- `region_price_stat`
- `building_price_stat`
- `property_score_stat`
- `properties`

It does not truncate existing rows by default. It accumulates and updates rows
based on each table's unique keys.

## Local Environment

Keep secrets in ignored `.env` files:

```env
MOLIT_SERVICE_KEY=
NAVER_MAPS_CLIENT_ID=
NAVER_MAPS_CLIENT_SECRET=
SUPABASE_DB_URL=
SUPABASE_DB_USERNAME=
SUPABASE_DB_PASSWORD=
```

`SUPABASE_DB_URL` may be either `jdbc:postgresql://...` or
`postgresql://...`.

## Generated Data

Generated files under `data/raw/`, `data/seed/`, `data/pipeline/`, and
`database/seed/` are local artifacts and should not be committed.

Use `scripts/data_pipeline/README.md` for the current nationwide 12-month data
collection and Supabase load workflow.
