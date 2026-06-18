# Seed Data

## F-1 Property Seed Flow

F-1 uses dummy property rows generated on top of real building anchors extracted from MOLIT real-transaction XML data.

The input transaction rows are normalized first, then geocoded once during seed generation. The frontend never calls geocoding or public transaction APIs at runtime.

## Files

- `../raw/molit/manifest.json`: list of downloaded MOLIT XML files and region metadata.
- `transaction-history.seed.json`: normalized transaction rows collected from the 8 MOLIT APIs.
- `geocoding-cache.json`: address or building key to latitude/longitude cache.
- `properties.seed.json`: generated dummy properties for map markers and property detail.

## Retention Policy

These files are **F-1 bootstrap seed artifacts**. They are committed for now so every teammate can reproduce the same Supabase seed state while the Spring Batch ingestion feature does not exist yet.

| File | Keep now? | Why | Remove when |
| --- | --- | --- | --- |
| `transaction-history.seed.json` | Yes | Reproducible normalized MOLIT transaction input for SQL seed generation | Spring Batch stores MOLIT rows directly in `transaction_history` |
| `geocoding-cache.json` | Yes | Avoids repeatedly calling Naver Geocoding for the same building anchors | Batch owns geocoding cache/upsert behavior |
| `properties.seed.json` | Yes | Reproducible F-1 dummy map listings for BE/FE development | Production-like property ingestion or batch-generated dummy data replaces it |

Do not treat these files as the production ingestion mechanism. They are a temporary bootstrap dataset for F-1 map/API development.

## Generate

Normalize saved MOLIT XML files:

```bash
python scripts/seed/fetch_molit_transactions.py --dry-run
python scripts/seed/fetch_molit_transactions.py
python scripts/seed/normalize_molit_transactions.py --manifest data/raw/molit/manifest.json
```

Generate SQL seed files from normalized transactions and geocoding cache:

```bash
python scripts/seed/geocode_property_anchors.py --dry-run
python scripts/seed/geocode_property_anchors.py
python scripts/seed/generate_properties_seed.py
```

The generator writes:

- `database/seed/transaction_history_seed.sql`
- `database/seed/properties_seed.sql`
- `database/seed/chunks/transaction_history_seed_*.sql`
- `database/seed/chunks/properties_seed_*.sql`

Only coordinates with `BUILDING_EXACT` or `ADDRESS_EXACT` quality are used for F-1 property markers.
