# Seed Data

## F-1 Property Seed Flow

F-1 uses dummy property rows generated on top of real building anchors extracted from MOLIT real-transaction XML data.

The input transaction rows are normalized first, then geocoded once during seed generation. The frontend never calls geocoding or public transaction APIs at runtime.

## Files

- `../raw/molit/manifest.json`: list of downloaded MOLIT XML files and region metadata.
- `transaction-history.seed.json`: normalized transaction rows collected from the 8 MOLIT APIs.
- `geocoding-cache.json`: address or building key to latitude/longitude cache.
- `properties.seed.json`: generated dummy properties for map markers and property detail.

## Generate

Normalize saved MOLIT XML files:

```bash
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

Only coordinates with `BUILDING_EXACT` or `ADDRESS_EXACT` quality are used for F-1 property markers.
