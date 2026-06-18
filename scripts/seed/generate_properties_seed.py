import hashlib
import json
import random
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NORMALIZED_TRANSACTIONS_PATH = ROOT / "data" / "seed" / "transaction-history.seed.json"
GEOCODING_CACHE_PATH = ROOT / "data" / "seed" / "geocoding-cache.json"
PROPERTIES_OUTPUT_PATH = ROOT / "data" / "seed" / "properties.seed.json"
TRANSACTION_SQL_OUTPUT_PATH = ROOT / "database" / "seed" / "transaction_history_seed.sql"
PROPERTY_SQL_OUTPUT_PATH = ROOT / "database" / "seed" / "properties_seed.sql"
SQL_CHUNK_DIR = ROOT / "database" / "seed" / "chunks"
RANDOM_SEED = 20260616
TRANSACTION_SQL_CHUNK_SIZE = 500
PROPERTY_SQL_CHUNK_SIZE = 500


PROPERTY_TYPE_LABELS = {
    "ONE_ROOM": "원룸",
    "OFFICETEL": "오피스텔",
    "VILLA": "빌라",
    "APARTMENT": "아파트",
    "MULTI_FAMILY": "다가구",
}

RENT_PROPERTY_TYPES = {"OFFICETEL", "VILLA", "APARTMENT", "MULTI_FAMILY"}
SALE_PROPERTY_TYPES = {"OFFICETEL", "VILLA", "APARTMENT", "MULTI_FAMILY"}


def read_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def decimal_money(value):
    return Decimal(str(value or 0))


def round_money(value, unit):
    number = decimal_money(value)
    rounded = (number / unit).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * unit
    return int(rounded)


def sql_value(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    if isinstance(value, (dict, list)):
        escaped = json.dumps(value, ensure_ascii=False).replace("'", "''")
        return f"'{escaped}'::jsonb"
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def normalize_items(payload):
    if isinstance(payload, list):
        return payload
    return payload.get("items", [])


def deduplicate_transactions(transactions):
    seen = set()
    unique = []
    for tx in transactions:
        key = (tx.get("source_api"), tx.get("source_transaction_key"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(tx)
    return unique


def group_by_building(transactions):
    groups = {}
    for tx in transactions:
        if tx.get("building_key"):
            groups.setdefault(tx["building_key"], []).append(tx)
    return groups


def median(values):
    ordered = sorted(values)
    if not ordered:
        return None
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def representative_transaction(transactions):
    return sorted(
        transactions,
        key=lambda tx: (
            tx.get("contract_year_month") or "",
            int(tx.get("contract_day") or 0),
        ),
        reverse=True,
    )[0]


def coordinate_for(anchor, geocoding_cache):
    candidates = [
        anchor.get("building_key"),
        anchor.get("address"),
        " ".join(
            value
            for value in [
                anchor.get("sido"),
                anchor.get("sigungu"),
                anchor.get("dong"),
                anchor.get("jibun"),
            ]
            if value
        ),
        " ".join(
            value
            for value in [
                anchor.get("sido"),
                anchor.get("sigungu"),
                anchor.get("dong"),
                anchor.get("building_name"),
            ]
            if value
        ),
    ]
    for key in candidates:
        if key and key in geocoding_cache:
            return geocoding_cache[key]
    return None


def price_from_transactions(transactions, transaction_type):
    same_type = [tx for tx in transactions if tx["transaction_type"] == transaction_type]
    if not same_type:
        return None
    if transaction_type == "MONTHLY_RENT":
        deposits = [tx["deposit"] for tx in same_type if tx.get("deposit") is not None]
        rents = [tx["monthly_rent"] for tx in same_type if tx.get("monthly_rent") is not None]
        if not deposits or not rents:
            return None
        return {
            "deposit": round_money(decimal_money(median(deposits)) * Decimal(str(random.uniform(0.95, 1.10))), Decimal("1000000")),
            "monthly_rent": round_money(decimal_money(median(rents)) * Decimal(str(random.uniform(0.95, 1.10))), Decimal("10000")),
            "price": None,
        }
    if transaction_type == "JEONSE":
        deposits = [tx["deposit"] for tx in same_type if tx.get("deposit") is not None]
        if not deposits:
            return None
        return {
            "deposit": round_money(decimal_money(median(deposits)) * Decimal(str(random.uniform(0.95, 1.10))), Decimal("1000000")),
            "monthly_rent": None,
            "price": None,
        }
    prices = [tx["price"] for tx in same_type if tx.get("price") is not None]
    if not prices:
        return None
    return {
        "deposit": None,
        "monthly_rent": None,
        "price": round_money(decimal_money(median(prices)) * Decimal(str(random.uniform(0.95, 1.10))), Decimal("10000000")),
    }


def transaction_type_candidates(property_type, transactions):
    candidates = []
    existing = {tx["transaction_type"] for tx in transactions}
    if property_type in RENT_PROPERTY_TYPES:
        candidates.extend(tx for tx in ("MONTHLY_RENT", "JEONSE") if tx in existing)
    if property_type in SALE_PROPERTY_TYPES and "SALE" in existing:
        candidates.append("SALE")
    return candidates


def build_property(anchor, transactions, sequence, geocoding_cache):
    coords = coordinate_for(anchor, geocoding_cache)
    if not coords or coords.get("quality") not in ("BUILDING_EXACT", "ADDRESS_EXACT"):
        return None

    property_type = anchor["property_type"]
    candidates = transaction_type_candidates(property_type, transactions)
    if not candidates:
        return None

    transaction_type = random.choice(candidates)
    price_fields = price_from_transactions(transactions, transaction_type)
    if not price_fields:
        return None

    rep = representative_transaction(transactions)
    area_m2 = rep["area_m2"]
    building_name = anchor.get("building_name")
    label = PROPERTY_TYPE_LABELS.get(property_type, "주택")
    title_name = building_name or f"{anchor['dong']} {label}"
    source_key = hashlib.sha1(anchor["building_key"].encode("utf-8")).hexdigest()[:16]
    source_property_id = f"synthetic-{source_key}-{sequence:03d}"

    return {
        "title": f"{title_name} {label}",
        "building_name": building_name,
        "building_key": anchor["building_key"],
        "anchor_transaction_key": rep["source_transaction_key"],
        "property_type": property_type,
        "transaction_type": transaction_type,
        "deposit": price_fields["deposit"],
        "monthly_rent": price_fields["monthly_rent"],
        "price": price_fields["price"],
        "maintenance_fee": round_money(random.randint(5, 25) * 10000, Decimal("10000")),
        "area_m2": area_m2,
        "floor": rep.get("floor"),
        "total_floor": None,
        "address": anchor["address"],
        "road_address": anchor.get("road_address"),
        "sido": anchor["sido"],
        "sigungu": anchor["sigungu"],
        "dong": anchor["dong"],
        "legal_dong_code": anchor["legal_dong_code"],
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "geocoding_provider": coords.get("provider"),
        "geocoding_quality": coords["quality"],
        "geocoded_at": coords.get("geocoded_at"),
        "description": "실거래가 건물 정보를 기준으로 생성한 MVP 더미 매물입니다.",
        "source": "MVP_SYNTHETIC",
        "source_property_id": source_property_id,
        "source_url": None,
        "crawled_at": None,
        "registered_at": datetime.now(timezone.utc).date().isoformat(),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def anchors_from_transactions(transactions):
    anchors = []
    for building_key, rows in group_by_building(transactions).items():
        rep = representative_transaction(rows)
        address_parts = [rep.get("sido"), rep.get("sigungu"), rep.get("dong"), rep.get("jibun")]
        address = " ".join(part for part in address_parts if part)
        anchors.append(
            {
                "building_key": building_key,
                "building_name": rep.get("building_name"),
                "property_type": rep["property_type"],
                "sido": rep["sido"],
                "sigungu": rep["sigungu"],
                "dong": rep["dong"],
                "legal_dong_code": rep["legal_dong_code"],
                "jibun": rep.get("jibun"),
                "address": address,
                "road_address": rep.get("road_address"),
            }
        )
    return anchors


def generate_properties(transactions, geocoding_cache):
    random.seed(RANDOM_SEED)
    properties = []
    for sequence, anchor in enumerate(anchors_from_transactions(transactions), start=1):
        generated = build_property(anchor, group_by_building(transactions)[anchor["building_key"]], sequence, geocoding_cache)
        if generated:
            properties.append(generated)
    return properties


def write_json(properties):
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": "MVP_SYNTHETIC",
        "totalCount": len(properties),
        "items": properties,
    }
    PROPERTIES_OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def chunks(items, size):
    for start in range(0, len(items), size):
        yield start // size + 1, items[start : start + size]


def clean_chunk_files(prefix):
    SQL_CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    for path in SQL_CHUNK_DIR.glob(f"{prefix}_*.sql"):
        path.unlink()


def write_chunk_index(transaction_count, property_count):
    lines = [
        "# Seed SQL Chunks",
        "",
        "Supabase SQL Editor may reject very large SQL files. Run these chunk files in order.",
        "",
        "1. Run all `transaction_history_seed_*.sql` files in numeric order.",
        "2. Run all `properties_seed_*.sql` files in numeric order.",
        "",
        f"- transaction chunks: {transaction_count}",
        f"- property chunks: {property_count}",
        "",
    ]
    (SQL_CHUNK_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def transaction_sql_lines(transactions, columns):
    lines = [
        "-- F-1 seed input normalized from MOLIT real-transaction XML APIs.",
        "insert into public.transaction_history (",
        "    " + ",\n    ".join(columns),
        ") values",
    ]
    value_lines = []
    for item in transactions:
        values = ", ".join(sql_value(item.get(column)) for column in columns)
        value_lines.append(f"    ({values})")
    lines.append(",\n".join(value_lines))
    lines.append(
        "on conflict (source_api, source_transaction_key) do update set\n"
        "    property_type = excluded.property_type,\n"
        "    transaction_type = excluded.transaction_type,\n"
        "    sido = excluded.sido,\n"
        "    sigungu = excluded.sigungu,\n"
        "    dong = excluded.dong,\n"
        "    legal_dong_code = excluded.legal_dong_code,\n"
        "    jibun = excluded.jibun,\n"
        "    building_name = excluded.building_name,\n"
        "    building_key = excluded.building_key,\n"
        "    contract_year_month = excluded.contract_year_month,\n"
        "    contract_day = excluded.contract_day,\n"
        "    deposit = excluded.deposit,\n"
        "    monthly_rent = excluded.monthly_rent,\n"
        "    price = excluded.price,\n"
        "    area_m2 = excluded.area_m2,\n"
        "    floor = excluded.floor,\n"
        "    build_year = excluded.build_year,\n"
        "    raw_json = excluded.raw_json;"
    )
    return lines


def write_transaction_sql(transactions):
    if not transactions:
        TRANSACTION_SQL_OUTPUT_PATH.write_text(
            "-- No transaction_history seed rows. Populate data/seed/transaction-history.seed.json first.\n",
            encoding="utf-8",
        )
        clean_chunk_files("transaction_history_seed")
        write_chunk_index(0, 0)
        return

    columns = [
        "source_api",
        "source_transaction_key",
        "property_type",
        "transaction_type",
        "sido",
        "sigungu",
        "dong",
        "legal_dong_code",
        "jibun",
        "building_name",
        "building_key",
        "contract_year_month",
        "contract_day",
        "deposit",
        "monthly_rent",
        "price",
        "area_m2",
        "floor",
        "build_year",
        "raw_json",
    ]
    lines = transaction_sql_lines(transactions, columns)
    TRANSACTION_SQL_OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    clean_chunk_files("transaction_history_seed")
    for index, chunk in chunks(transactions, TRANSACTION_SQL_CHUNK_SIZE):
        chunk_path = SQL_CHUNK_DIR / f"transaction_history_seed_{index:03d}.sql"
        chunk_path.write_text("\n".join(transaction_sql_lines(chunk, columns)) + "\n", encoding="utf-8")


def property_sql_lines(properties, columns):
    lines = [
        "-- F-1 MVP dummy properties generated from transaction building anchors.",
        "insert into public.properties (",
        "    " + ",\n    ".join(columns),
        ") values",
    ]
    value_lines = []
    for item in properties:
        values = []
        for column in columns:
            if column == "anchor_transaction_id":
                values.append(
                    "(select id from public.transaction_history where source_transaction_key = "
                    f"{sql_value(item['anchor_transaction_key'])} limit 1)"
                )
            else:
                values.append(sql_value(item.get(column)))
        value_lines.append(f"    ({', '.join(values)})")
    lines.append(",\n".join(value_lines))
    lines.append(
        "on conflict (source, source_property_id) do update set\n"
        "    title = excluded.title,\n"
        "    building_name = excluded.building_name,\n"
        "    building_key = excluded.building_key,\n"
        "    anchor_transaction_id = excluded.anchor_transaction_id,\n"
        "    property_type = excluded.property_type,\n"
        "    transaction_type = excluded.transaction_type,\n"
        "    deposit = excluded.deposit,\n"
        "    monthly_rent = excluded.monthly_rent,\n"
        "    price = excluded.price,\n"
        "    maintenance_fee = excluded.maintenance_fee,\n"
        "    area_m2 = excluded.area_m2,\n"
        "    floor = excluded.floor,\n"
        "    total_floor = excluded.total_floor,\n"
        "    address = excluded.address,\n"
        "    road_address = excluded.road_address,\n"
        "    sido = excluded.sido,\n"
        "    sigungu = excluded.sigungu,\n"
        "    dong = excluded.dong,\n"
        "    legal_dong_code = excluded.legal_dong_code,\n"
        "    latitude = excluded.latitude,\n"
        "    longitude = excluded.longitude,\n"
        "    geocoding_provider = excluded.geocoding_provider,\n"
        "    geocoding_quality = excluded.geocoding_quality,\n"
        "    geocoded_at = excluded.geocoded_at,\n"
        "    description = excluded.description,\n"
        "    source_url = excluded.source_url,\n"
        "    crawled_at = excluded.crawled_at,\n"
        "    registered_at = excluded.registered_at,\n"
        "    is_active = excluded.is_active,\n"
        "    updated_at = excluded.updated_at;"
    )
    return lines


def write_property_sql(properties):
    if not properties:
        PROPERTY_SQL_OUTPUT_PATH.write_text(
            "-- No properties seed rows. Populate transaction seed rows and geocoding-cache.json first.\n",
            encoding="utf-8",
        )
        clean_chunk_files("properties_seed")
        return

    columns = [
        "title",
        "building_name",
        "building_key",
        "anchor_transaction_id",
        "property_type",
        "transaction_type",
        "deposit",
        "monthly_rent",
        "price",
        "maintenance_fee",
        "area_m2",
        "floor",
        "total_floor",
        "address",
        "road_address",
        "sido",
        "sigungu",
        "dong",
        "legal_dong_code",
        "latitude",
        "longitude",
        "geocoding_provider",
        "geocoding_quality",
        "geocoded_at",
        "description",
        "source",
        "source_property_id",
        "source_url",
        "crawled_at",
        "registered_at",
        "is_active",
        "created_at",
        "updated_at",
    ]
    lines = property_sql_lines(properties, columns)
    PROPERTY_SQL_OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    clean_chunk_files("properties_seed")
    for index, chunk in chunks(properties, PROPERTY_SQL_CHUNK_SIZE):
        chunk_path = SQL_CHUNK_DIR / f"properties_seed_{index:03d}.sql"
        chunk_path.write_text("\n".join(property_sql_lines(chunk, columns)) + "\n", encoding="utf-8")


def main():
    transactions = deduplicate_transactions(normalize_items(read_json(NORMALIZED_TRANSACTIONS_PATH, {"items": []})))
    geocoding_cache = read_json(GEOCODING_CACHE_PATH, {})
    properties = generate_properties(transactions, geocoding_cache)
    write_json(properties)
    write_transaction_sql(transactions)
    write_property_sql(properties)
    transaction_chunk_count = (len(transactions) + TRANSACTION_SQL_CHUNK_SIZE - 1) // TRANSACTION_SQL_CHUNK_SIZE
    property_chunk_count = (len(properties) + PROPERTY_SQL_CHUNK_SIZE - 1) // PROPERTY_SQL_CHUNK_SIZE
    write_chunk_index(transaction_chunk_count, property_chunk_count)
    print(f"loaded {len(transactions)} transaction rows")
    print(f"generated {len(properties)} properties")
    print(PROPERTIES_OUTPUT_PATH)
    print(TRANSACTION_SQL_OUTPUT_PATH)
    print(PROPERTY_SQL_OUTPUT_PATH)
    print(SQL_CHUNK_DIR)


if __name__ == "__main__":
    main()
