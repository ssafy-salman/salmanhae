# MOLIT Raw XML

Place downloaded MOLIT real-transaction XML responses in this directory and list them in `manifest.json`.

The normalizer does not call external APIs. It only converts saved XML files into `data/seed/transaction-history.seed.json`.

```bash
python scripts/seed/normalize_molit_transactions.py --manifest data/raw/molit/manifest.json
```

Each manifest entry must include the source API type and the region metadata used for the original API request. MOLIT APIs are queried by `LAWD_CD` and `DEAL_YMD`, while the XML item itself does not always contain the full 시/도 and 시/군/구 names.

`*.xml` and `manifest.json` are local seed inputs and are ignored by git. Commit only `manifest.example.json` and this README.

Production ingestion should not store XML files in the repository. Spring Batch will call the MOLIT APIs, parse XML responses, and insert normalized rows into `transaction_history` directly.
