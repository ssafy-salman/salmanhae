# Offline Data Pipeline

This pipeline builds the MVP real-estate dataset without using Spring Batch.
It fetches MOLIT real-transaction XML responses, normalizes transactions,
computes price statistics, generates synthetic properties from real building
anchors, and upserts everything into Supabase PostgreSQL.

## Scope

- Region scope: nationwide, based on a `lawd-codes.csv` file
- Time scope: recent 12 months by default
- Source APIs: apartment, officetel, villa/row-house, and multi-family rent/sale
- Property generation: 1 to 2 synthetic properties per geocoded building anchor
- Geocoding failure policy: keep transaction rows, skip property generation
- DB policy: upsert and accumulate, never truncate by default

## Environment

The script reads environment files in this order and never requires secrets in
Git:

1. `.env`
2. `.env.local`
3. `backend/.env`
4. `backend/.env.local`
5. `scripts/.env`
6. `scripts/.env.local`

Required keys:

```env
MOLIT_SERVICE_KEY=
NAVER_MAPS_CLIENT_ID=
NAVER_MAPS_CLIENT_SECRET=
SUPABASE_DB_URL=
SUPABASE_DB_USERNAME=
SUPABASE_DB_PASSWORD=
```

`SUPABASE_DB_URL` may be either a JDBC URL or a PostgreSQL URL.

## Lawd Codes

Nationwide collection needs a CSV file with one row per 시군구.

Recommended path:

```text
data/reference/lawd-codes.csv
```

Supported CSV formats:

```csv
lawd_cd,sido,sigungu
11680,서울특별시,강남구
```

or a 법정동 코드 file with columns such as `법정동코드`, `법정동명`, `폐지여부`.
The pipeline derives active 시군구 rows from 10-digit legal-dong codes ending in
`00000`.

## Commands

Smoke plan:

```bash
python scripts/data_pipeline/pipeline.py plan --months 12 --limit-regions 3
```

Fetch a small sample:

```bash
python scripts/data_pipeline/pipeline.py fetch --months 1 --limit-regions 1 --source-apis MOLIT_APT_RENT
```

Run a resumable nationwide pipeline:

```bash
python scripts/data_pipeline/pipeline.py run --months 12 --scope nationwide --migrate-db --load-db
```

Verify DB counts:

```bash
python scripts/data_pipeline/pipeline.py verify-db
```

Apply migrations only:

```bash
python scripts/data_pipeline/pipeline.py migrate-db
```

Install DB driver when local Python does not have one:

```bash
python -m pip install -r scripts/data_pipeline/requirements.txt
```

## Generated Artifacts

The pipeline writes resumable local outputs under `data/pipeline/`.

```text
data/pipeline/raw/                 # fetched MOLIT XML responses
data/pipeline/normalized/          # transaction_history.jsonl
data/pipeline/generated/           # stats and property JSONL files
data/pipeline/cache/               # geocoding-cache.json
data/pipeline/manifest.json        # fetched page manifest
data/pipeline/errors.json          # recoverable fetch/geocoding errors
```

Older bootstrap outputs under `data/raw/`, `data/seed/`, and `database/seed/`
are no longer the source of truth. Keep them out of git. The current source of
truth is the migration SQL plus this pipeline, which can recreate and upsert
the dataset.

When this logic is moved into Spring Scheduler or another production job, these
local generated outputs can be deleted without a schema change.
