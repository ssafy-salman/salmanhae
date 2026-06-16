# MOLIT Raw XML

Place downloaded MOLIT real-transaction XML responses in this directory and list them in `manifest.json`.

The fetcher calls MOLIT APIs and stores XML responses as local raw cache files. The normalizer then converts saved XML files into `data/seed/transaction-history.seed.json`.

Copy `fetch-plan.example.json` to `fetch-plan.json`, adjust regions/months/source APIs, and run:

```bash
python scripts/seed/fetch_molit_transactions.py --dry-run
python scripts/seed/fetch_molit_transactions.py
```

```bash
python scripts/seed/normalize_molit_transactions.py --manifest data/raw/molit/manifest.json
```

Each manifest entry must include the source API type and the region metadata used for the original API request. MOLIT APIs are queried by `LAWD_CD` and `DEAL_YMD`, while the XML item itself does not always contain the full 시/도 and 시/군/구 names.

`*.xml` and `manifest.json` are local seed inputs and are ignored by git. Commit only `manifest.example.json` and this README.

Production ingestion should not store XML files in the repository. Spring Batch will call the MOLIT APIs, parse XML responses, and insert normalized rows into `transaction_history` directly.
