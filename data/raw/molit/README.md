# MOLIT Raw XML

Place downloaded MOLIT real-transaction XML responses in this directory and list them in `manifest.json`.

The normalizer does not call external APIs. It only converts saved XML files into `data/seed/transaction-history.seed.json`.

```bash
python scripts/seed/normalize_molit_transactions.py --manifest data/raw/molit/manifest.json
```

Each manifest entry must include the source API type and the region metadata used for the original API request. MOLIT APIs are queried by `LAWD_CD` and `DEAL_YMD`, while the XML item itself does not always contain the full 시/도 and 시/군/구 names.
