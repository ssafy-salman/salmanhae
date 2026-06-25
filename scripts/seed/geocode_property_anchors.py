import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, parse, request


ROOT = Path(__file__).resolve().parents[2]
TRANSACTION_SEED_PATH = ROOT / "data" / "seed" / "transaction-history.seed.json"
GEOCODING_CACHE_PATH = ROOT / "data" / "seed" / "geocoding-cache.json"
NAVER_GEOCODING_URL = "https://maps.apigw.ntruss.com/map-geocode/v2/geocode"


def read_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_env_file(path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_local_env():
    load_env_file(ROOT / ".env.local")
    load_env_file(ROOT / ".env")


def transaction_items(payload):
    if isinstance(payload, list):
        return payload
    return payload.get("items", [])


def anchor_key(row):
    return row.get("building_key")


def compact_join(parts):
    return " ".join(str(part).strip() for part in parts if part not in (None, ""))


def query_candidates(row):
    building_query = compact_join([row.get("sido"), row.get("sigungu"), row.get("dong"), row.get("building_name")])
    address_query = compact_join([row.get("sido"), row.get("sigungu"), row.get("dong"), row.get("jibun")])
    candidates = []
    if row.get("building_name") and building_query:
        candidates.append({"query": building_query, "quality": "BUILDING_EXACT"})
    if row.get("jibun") and address_query:
        candidates.append({"query": address_query, "quality": "ADDRESS_EXACT"})
    return candidates


def collect_anchors(transactions):
    anchors = {}
    for row in transactions:
        key = anchor_key(row)
        if not key or key in anchors:
            continue
        candidates = query_candidates(row)
        if not candidates:
            continue
        anchors[key] = {
            "building_key": key,
            "building_name": row.get("building_name"),
            "address": compact_join([row.get("sido"), row.get("sigungu"), row.get("dong"), row.get("jibun")]),
            "queries": candidates,
        }
    return anchors


def parse_naver_response(data, quality, query):
    addresses = data.get("addresses") or []
    if not addresses:
        return None
    first = addresses[0]
    x = first.get("x")
    y = first.get("y")
    if x is None or y is None:
        return None
    return {
        "latitude": round(float(y), 7),
        "longitude": round(float(x), 7),
        "provider": "NAVER",
        "quality": quality,
        "query": query,
        "road_address": first.get("roadAddress") or None,
        "jibun_address": first.get("jibunAddress") or None,
        "geocoded_at": datetime.now(timezone.utc).isoformat(),
    }


def naver_geocode(query, client_id, client_secret, timeout=10):
    url = f"{NAVER_GEOCODING_URL}?{parse.urlencode({'query': query})}"
    req = request.Request(
        url,
        headers={
            "x-ncp-apigw-api-key-id": client_id,
            "x-ncp-apigw-api-key": client_secret,
            "Accept": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Naver geocoding failed ({exc.code}): {message}") from exc


def geocode_anchor(anchor, client_id, client_secret):
    for candidate in anchor["queries"]:
        data = naver_geocode(candidate["query"], client_id, client_secret)
        parsed = parse_naver_response(data, candidate["quality"], candidate["query"])
        if parsed:
            return parsed
    return {
        "provider": "NAVER",
        "quality": "FAILED",
        "query": anchor["queries"][0]["query"],
        "geocoded_at": datetime.now(timezone.utc).isoformat(),
    }


def update_cache(transactions, cache, client_id, client_secret, dry_run=False, limit=None, sleep_seconds=0.1):
    anchors = collect_anchors(transactions)
    pending = [anchor for key, anchor in anchors.items() if key not in cache]
    if limit is not None:
        pending = pending[:limit]

    results = []
    for anchor in pending:
        if dry_run:
            results.append({"building_key": anchor["building_key"], "queries": anchor["queries"]})
            continue
        cache[anchor["building_key"]] = geocode_anchor(anchor, client_id, client_secret)
        results.append({"building_key": anchor["building_key"], "result": cache[anchor["building_key"]]})
        time.sleep(sleep_seconds)
    return results


def parse_args():
    parser = argparse.ArgumentParser(description="Build geocoding cache for F-1 transaction building anchors.")
    parser.add_argument("--transactions", type=Path, default=TRANSACTION_SEED_PATH)
    parser.add_argument("--cache", type=Path, default=GEOCODING_CACHE_PATH)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--sleep", type=float, default=0.1)
    return parser.parse_args()


def main():
    args = parse_args()
    load_local_env()
    transactions = transaction_items(read_json(args.transactions, {"items": []}))
    cache = read_json(args.cache, {})
    client_id = os.environ.get("NAVER_MAPS_CLIENT_ID")
    client_secret = os.environ.get("NAVER_MAPS_CLIENT_SECRET")

    if not args.dry_run and (not client_id or not client_secret):
        raise SystemExit("NAVER_MAPS_CLIENT_ID and NAVER_MAPS_CLIENT_SECRET are required.")

    results = update_cache(
        transactions,
        cache,
        client_id,
        client_secret,
        dry_run=args.dry_run,
        limit=args.limit,
        sleep_seconds=args.sleep,
    )
    if not args.dry_run:
        write_json(args.cache, cache)

    print(f"loaded {len(transactions)} transaction rows")
    print(f"processed {len(results)} geocoding targets")
    print(args.cache)


if __name__ == "__main__":
    main()
