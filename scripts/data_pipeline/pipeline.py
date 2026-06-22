import argparse
import csv
import hashlib
import json
import math
import os
import random
import time
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from urllib import error, parse, request

from defusedxml.ElementTree import fromstring as parse_xml_text
from defusedxml.ElementTree import parse as parse_xml_file


ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = ROOT / "data" / "pipeline"
MIGRATIONS_DIR = ROOT / "database" / "migrations"
DEFAULT_LAWD_CODES = ROOT / "data" / "reference" / "lawd-codes.csv"
GEOCODING_CACHE = WORK_DIR / "cache" / "geocoding-cache.json"
MANIFEST_PATH = WORK_DIR / "manifest.json"
ERRORS_PATH = WORK_DIR / "errors.json"
TRANSACTIONS_JSONL = WORK_DIR / "normalized" / "transaction_history.jsonl"
PROPERTIES_JSONL = WORK_DIR / "generated" / "properties.jsonl"
REGION_STATS_JSONL = WORK_DIR / "generated" / "region_price_stat.jsonl"
BUILDING_STATS_JSONL = WORK_DIR / "generated" / "building_price_stat.jsonl"
RANDOM_SEED = 20260623


SOURCE_CONFIG = {
    "MOLIT_APT_RENT": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent",
        "file_prefix": "apt-rent",
        "property_type": "APARTMENT",
        "mode": "RENT",
    },
    "MOLIT_OFFICETEL_RENT": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcOffiRent/getRTMSDataSvcOffiRent",
        "file_prefix": "officetel-rent",
        "property_type": "OFFICETEL",
        "mode": "RENT",
    },
    "MOLIT_VILLA_RENT": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcRHRent/getRTMSDataSvcRHRent",
        "file_prefix": "villa-rent",
        "property_type": "VILLA",
        "mode": "RENT",
    },
    "MOLIT_MULTI_FAMILY_RENT": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent",
        "file_prefix": "multi-family-rent",
        "property_type": "MULTI_FAMILY",
        "mode": "RENT",
    },
    "MOLIT_APT_SALE": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev",
        "file_prefix": "apt-sale",
        "property_type": "APARTMENT",
        "mode": "SALE",
    },
    "MOLIT_OFFICETEL_SALE": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcOffiTrade/getRTMSDataSvcOffiTrade",
        "file_prefix": "officetel-sale",
        "property_type": "OFFICETEL",
        "mode": "SALE",
    },
    "MOLIT_VILLA_SALE": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade",
        "file_prefix": "villa-sale",
        "property_type": "VILLA",
        "mode": "SALE",
    },
    "MOLIT_MULTI_FAMILY_SALE": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade",
        "file_prefix": "multi-family-sale",
        "property_type": "MULTI_FAMILY",
        "mode": "SALE",
    },
}


FIELD_ALIASES = {
    "dong": ["umdNm", "dong"],
    "umd_code": ["umdCd"],
    "jibun": ["jibun", "bonbun"],
    "bonbun": ["bonbun"],
    "bubun": ["bubun"],
    "building_name": ["aptNm", "offiNm", "mhouseNm", "houseNm", "danjiNm"],
    "area_m2": ["excluUseAr", "dealArea", "area", "totalFloorAr"],
    "floor": ["floor"],
    "build_year": ["buildYear"],
    "deal_year": ["dealYear"],
    "deal_month": ["dealMonth"],
    "deal_day": ["dealDay"],
    "contract_year_month": ["contractYearMonth"],
    "deposit": ["deposit", "rentDeposit"],
    "monthly_rent": ["monthlyRent", "rentFee"],
    "price": ["dealAmount", "dealAmt"],
    "road_address": ["roadNm", "roadnm"],
}


def load_env_file(path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_env():
    for relative in [".env", ".env.local", "backend/.env", "backend/.env.local", "scripts/.env", "scripts/.env.local"]:
        load_env_file(ROOT / relative)


def ensure_dir(path):
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    ensure_dir(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path, rows):
    ensure_dir(path)
    with path.open("a", encoding="utf-8") as fp:
        for row in rows:
            fp.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path):
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def recent_months(count, today=None):
    current = today or datetime.now()
    year = current.year
    month = current.month
    months = []
    for _ in range(count):
        months.append(f"{year:04d}{month:02d}")
        month -= 1
        if month == 0:
            year -= 1
            month = 12
    return months


def csv_value(row, *names):
    lowered = {key.lower(): value for key, value in row.items() if key is not None}
    for name in names:
        if name in row and row[name]:
            return row[name].strip()
        lowered_value = lowered.get(name.lower())
        if lowered_value:
            return lowered_value.strip()
    return ""


def load_lawd_codes(path):
    if not path.exists():
        raise SystemExit(f"LAWD code file not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))

    regions = {}
    for row in rows:
        lawd_cd = csv_value(row, "lawd_cd", "LAWD_CD")
        sido = csv_value(row, "sido", "SIDO")
        sigungu = csv_value(row, "sigungu", "SIGUNGU")
        if lawd_cd and sido and sigungu:
            regions[lawd_cd[:5]] = {"lawdCd": lawd_cd[:5], "sido": sido, "sigungu": sigungu}
            continue

        code = csv_value(row, "법정동코드", "code", "CODE")
        name = csv_value(row, "법정동명", "name", "NAME")
        deleted = csv_value(row, "폐지여부", "deleted", "DELETED")
        if not code or not name or deleted in ("폐지", "Y", "1", "true", "TRUE"):
            continue
        digits_only = "".join(ch for ch in code if ch.isdigit())
        if len(digits_only) != 10 or not digits_only.endswith("00000") or digits_only[2:5] == "000":
            continue
        parts = name.split()
        if len(parts) < 2:
            continue
        regions[digits_only[:5]] = {
            "lawdCd": digits_only[:5],
            "sido": parts[0],
            "sigungu": " ".join(parts[1:]),
        }

    return sorted(regions.values(), key=lambda item: item["lawdCd"])


def parse_csv_list(value):
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def service_key_param(service_key):
    return service_key if "%" in service_key else parse.quote(service_key, safe="")


def build_molit_url(config, service_key, lawd_cd, deal_ymd, page_no, num_of_rows):
    query = parse.urlencode(
        {
            "LAWD_CD": lawd_cd,
            "DEAL_YMD": deal_ymd,
            "pageNo": page_no,
            "numOfRows": num_of_rows,
        }
    )
    return f"{config['url']}?serviceKey={service_key_param(service_key)}&{query}"


def http_get_text(url, headers=None, timeout=60):
    req = request.Request(url, headers=headers or {})
    with request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def strip_namespace(tag):
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def parse_xml(xml_text):
    return parse_xml_text(xml_text.encode("utf-8"))


def find_text(root, tag_name, default=None):
    for element in root.iter():
        if strip_namespace(element.tag) == tag_name:
            return (element.text or "").strip()
    return default


def item_elements(root):
    return [element for element in root.iter() if strip_namespace(element.tag) == "item"]


def xml_item_to_dict(element):
    row = {}
    for child in list(element):
        row[strip_namespace(child.tag)] = (child.text or "").strip()
    return row


def first_value(row, field):
    for key in FIELD_ALIASES[field]:
        value = row.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return None


def digits(value):
    if value is None:
        return None
    found = [ch for ch in str(value).replace(",", "") if ch.isdigit()]
    return "".join(found) if found else None


def parse_decimal(value):
    if value in (None, ""):
        return None
    cleaned = str(value).replace(",", "").strip()
    try:
        return float(Decimal(cleaned))
    except InvalidOperation:
        return None


def parse_int(value):
    value_digits = digits(value)
    return int(value_digits) if value_digits else None


def parse_money_won(value):
    number = parse_int(value)
    return number * 10000 if number is not None else None


def normalize_jibun(row):
    direct = first_value(row, "jibun")
    if direct:
        return direct
    bonbun = digits(first_value(row, "bonbun"))
    bubun = digits(first_value(row, "bubun"))
    if not bonbun:
        return None
    bonbun = str(int(bonbun))
    if bubun and int(bubun) > 0:
        return f"{bonbun}-{int(bubun)}"
    return bonbun


def contract_parts(row):
    year_month = first_value(row, "contract_year_month")
    ym_digits = digits(year_month)
    if ym_digits and len(ym_digits) >= 6:
        return ym_digits[:6], parse_int(first_value(row, "deal_day"))
    year = parse_int(first_value(row, "deal_year"))
    month = parse_int(first_value(row, "deal_month"))
    day = parse_int(first_value(row, "deal_day"))
    if year and month:
        return f"{year:04d}{month:02d}", day
    return None, day


def legal_dong_code(row, manifest_entry):
    prefix = digits(manifest_entry.get("legalDongCodePrefix") or manifest_entry.get("lawdCd"))
    umd_code = digits(first_value(row, "umd_code"))
    if prefix and umd_code:
        return f"{prefix[:5]}{umd_code[-5:]}"[:10]
    return prefix[:10] if prefix else None


def building_key(normalized):
    parts = [
        normalized.get("legal_dong_code"),
        normalized.get("property_type"),
        normalized.get("building_name"),
        normalized.get("jibun"),
    ]
    return ":".join(str(part) for part in parts if part)


def source_transaction_key(normalized):
    fields = [
        "source_api",
        "legal_dong_code",
        "dong",
        "jibun",
        "building_name",
        "contract_year_month",
        "contract_day",
        "property_type",
        "transaction_type",
        "area_m2",
        "floor",
        "deposit",
        "monthly_rent",
        "price",
    ]
    raw_key = "|".join("" if normalized.get(field) is None else str(normalized.get(field)) for field in fields)
    return hashlib.sha1(raw_key.encode("utf-8")).hexdigest()


def normalize_row(row, manifest_entry):
    source_api = manifest_entry["sourceApi"]
    config = SOURCE_CONFIG[source_api]
    contract_year_month, contract_day = contract_parts(row)
    normalized = {
        "source_api": source_api,
        "source_transaction_key": "",
        "property_type": config["property_type"],
        "transaction_type": "SALE",
        "sido": manifest_entry["sido"],
        "sigungu": manifest_entry["sigungu"],
        "dong": first_value(row, "dong"),
        "legal_dong_code": legal_dong_code(row, manifest_entry),
        "jibun": normalize_jibun(row),
        "building_name": first_value(row, "building_name"),
        "building_key": "",
        "contract_year_month": contract_year_month,
        "contract_day": contract_day,
        "deposit": None,
        "monthly_rent": None,
        "price": None,
        "area_m2": parse_decimal(first_value(row, "area_m2")),
        "floor": parse_int(first_value(row, "floor")),
        "build_year": parse_int(first_value(row, "build_year")),
        "raw_json": row,
    }

    if config["mode"] == "RENT":
        normalized["deposit"] = parse_money_won(first_value(row, "deposit"))
        monthly_rent = parse_money_won(first_value(row, "monthly_rent"))
        normalized["monthly_rent"] = monthly_rent if monthly_rent and monthly_rent > 0 else None
        normalized["transaction_type"] = "MONTHLY_RENT" if normalized["monthly_rent"] else "JEONSE"
    else:
        normalized["price"] = parse_money_won(first_value(row, "price"))

    required = ["property_type", "transaction_type", "sido", "sigungu", "dong", "legal_dong_code", "contract_year_month", "area_m2"]
    if any(normalized.get(field) in (None, "") for field in required):
        return None
    if normalized["transaction_type"] == "SALE" and not normalized["price"]:
        return None
    if normalized["transaction_type"] == "JEONSE" and not normalized["deposit"]:
        return None
    if normalized["transaction_type"] == "MONTHLY_RENT" and (not normalized["deposit"] or not normalized["monthly_rent"]):
        return None

    normalized["building_key"] = building_key(normalized)
    if not normalized["building_key"]:
        return None
    normalized["source_transaction_key"] = source_transaction_key(normalized)
    return normalized


def planned_requests(regions, months, source_apis, limit_regions=None, limit_requests=None):
    selected_regions = regions[:limit_regions] if limit_regions else regions
    requests = []
    for source_api in source_apis:
        for region in selected_regions:
            for month in months:
                requests.append((source_api, region, month))
                if limit_requests and len(requests) >= limit_requests:
                    return requests
    return requests


def selected_source_apis(value):
    source_apis = parse_csv_list(value) or list(SOURCE_CONFIG.keys())
    unknown = [source_api for source_api in source_apis if source_api not in SOURCE_CONFIG]
    if unknown:
        valid = ", ".join(sorted(SOURCE_CONFIG))
        raise SystemExit(f"Unknown source API(s): {', '.join(unknown)}. Valid values: {valid}")
    return source_apis


def fetch_transactions(args):
    load_env()
    service_key = os.environ.get("MOLIT_SERVICE_KEY")
    if not service_key:
        raise SystemExit("MOLIT_SERVICE_KEY is required.")
    regions = load_lawd_codes(args.lawd_codes)
    months = parse_csv_list(args.month_values) or recent_months(args.months)
    source_apis = selected_source_apis(args.source_apis)
    requests_to_run = planned_requests(regions, months, source_apis, args.limit_regions, args.limit_requests)

    manifest = read_json(MANIFEST_PATH, {"files": []})
    errors = read_json(ERRORS_PATH, {"errors": []})
    seen_paths = {entry["xmlPath"] for entry in manifest["files"]}
    for index, (source_api, region, month) in enumerate(requests_to_run, start=1):
        config = SOURCE_CONFIG[source_api]
        page_no = 1
        while True:
            filename = f"{config['file_prefix']}-{region['lawdCd']}-{month}-p{page_no:04d}.xml"
            relative_path = f"raw/molit/{filename}"
            xml_path = WORK_DIR / relative_path
            entry = {
                "sourceApi": source_api,
                "xmlPath": relative_path,
                "sido": region["sido"],
                "sigungu": region["sigungu"],
                "legalDongCodePrefix": region["lawdCd"],
                "dealYmd": month,
                "pageNo": page_no,
            }
            print(f"[{index}/{len(requests_to_run)}] {source_api} {region['lawdCd']} {month} page {page_no}")
            if relative_path in seen_paths and xml_path.exists() and xml_path.stat().st_size > 0 and not args.no_skip_existing:
                root = parse_xml_file(str(xml_path)).getroot()
            else:
                url = build_molit_url(config, service_key, region["lawdCd"], month, page_no, args.num_of_rows)
                try:
                    xml_text = http_get_text(url, headers={"Accept": "application/xml"}, timeout=args.timeout)
                    ensure_dir(xml_path)
                    xml_path.write_text(xml_text, encoding="utf-8")
                    root = parse_xml(xml_text)
                    if relative_path not in seen_paths:
                        manifest["files"].append(entry)
                        seen_paths.add(relative_path)
                        write_json(MANIFEST_PATH, manifest)
                except Exception as exc:
                    errors["errors"].append({**entry, "error": str(exc)})
                    write_json(ERRORS_PATH, errors)
                    if args.fail_fast:
                        raise
                    break

            total_count = parse_int(find_text(root, "totalCount", "0")) or 0
            items_count = len(item_elements(root))
            if items_count == 0:
                break
            if total_count <= page_no * args.num_of_rows or items_count < args.num_of_rows:
                break
            page_no += 1
            time.sleep(args.sleep)
        time.sleep(args.sleep)

    print(f"manifest files: {len(manifest['files'])}")
    print(f"errors: {len(errors['errors'])}")


def normalize_manifest():
    manifest = read_json(MANIFEST_PATH, {"files": []})
    unique = {}
    for entry in manifest["files"]:
        xml_path = WORK_DIR / entry["xmlPath"]
        if not xml_path.exists():
            continue
        root = parse_xml_file(str(xml_path)).getroot()
        for item in item_elements(root):
            normalized = normalize_row(xml_item_to_dict(item), entry)
            if normalized:
                unique[(normalized["source_api"], normalized["source_transaction_key"])] = normalized
    rows = sorted(unique.values(), key=lambda row: (row["source_api"], row["source_transaction_key"]))
    ensure_dir(TRANSACTIONS_JSONL)
    TRANSACTIONS_JSONL.write_text("", encoding="utf-8")
    append_jsonl(TRANSACTIONS_JSONL, rows)
    print(f"normalized transactions: {len(rows)}")


def median(values):
    ordered = sorted(values)
    if not ordered:
        return None
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def average(values):
    return sum(values) / len(values) if values else None


def round_int(value):
    if value is None:
        return None
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def stat_money_fields(rows):
    deposits = [row["deposit"] for row in rows if row.get("deposit") is not None]
    rents = [row["monthly_rent"] for row in rows if row.get("monthly_rent") is not None]
    prices = [row["price"] for row in rows if row.get("price") is not None]
    months = [row["contract_year_month"] for row in rows if row.get("contract_year_month")]
    return {
        "avg_deposit": round_int(average(deposits)),
        "median_deposit": round_int(median(deposits)),
        "avg_monthly_rent": round_int(average(rents)),
        "median_monthly_rent": round_int(median(rents)),
        "avg_price": round_int(average(prices)),
        "median_price": round_int(median(prices)),
        "transaction_count": len(rows),
        "sample_from_ym": min(months) if months else None,
        "sample_to_ym": max(months) if months else None,
    }


def compute_stats():
    transactions = read_jsonl(TRANSACTIONS_JSONL)
    region_groups = defaultdict(list)
    building_groups = defaultdict(list)
    for row in transactions:
        for level, code, sido, sigungu, dong in row_region_keys(row):
            key = (level, code, sido, sigungu, dong, row["property_type"], row["transaction_type"])
            region_groups[key].append(row)
        building_key_value = (row["building_key"], row["property_type"], row["transaction_type"])
        building_groups[building_key_value].append(row)

    region_stats = []
    for (level, code, sido, sigungu, dong, property_type, transaction_type), rows in region_groups.items():
        region_stats.append(
            {
                "region_level": level,
                "region_code": code,
                "sido": sido,
                "sigungu": sigungu,
                "dong": dong,
                "property_type": property_type,
                "transaction_type": transaction_type,
                **stat_money_fields(rows),
            }
        )

    building_stats = []
    for (building_key_value, property_type, transaction_type), rows in building_groups.items():
        rep = sorted(rows, key=lambda item: (item.get("contract_year_month") or "", item.get("contract_day") or 0), reverse=True)[0]
        building_stats.append(
            {
                "building_key": building_key_value,
                "building_name": rep.get("building_name"),
                "sido": rep.get("sido"),
                "sigungu": rep.get("sigungu"),
                "dong": rep.get("dong"),
                "legal_dong_code": rep.get("legal_dong_code"),
                "property_type": property_type,
                "transaction_type": transaction_type,
                **stat_money_fields(rows),
            }
        )

    ensure_dir(REGION_STATS_JSONL)
    REGION_STATS_JSONL.write_text("", encoding="utf-8")
    append_jsonl(REGION_STATS_JSONL, region_stats)
    ensure_dir(BUILDING_STATS_JSONL)
    BUILDING_STATS_JSONL.write_text("", encoding="utf-8")
    append_jsonl(BUILDING_STATS_JSONL, building_stats)
    print(f"region price stats: {len(region_stats)}")
    print(f"building price stats: {len(building_stats)}")


def naver_geocode(query, timeout=20):
    client_id = os.environ.get("NAVER_MAPS_CLIENT_ID")
    client_secret = os.environ.get("NAVER_MAPS_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit("NAVER_MAPS_CLIENT_ID and NAVER_MAPS_CLIENT_SECRET are required.")
    url = "https://maps.apigw.ntruss.com/map-geocode/v2/geocode?" + parse.urlencode({"query": query})
    text = http_get_text(
        url,
        headers={
            "Accept": "application/json",
            "x-ncp-apigw-api-key-id": client_id,
            "x-ncp-apigw-api-key": client_secret,
        },
        timeout=timeout,
    )
    payload = json.loads(text)
    addresses = payload.get("addresses") or []
    if not addresses:
        return None
    first = addresses[0]
    return {
        "latitude": float(first["y"]),
        "longitude": float(first["x"]),
        "provider": "NAVER",
        "quality": "ADDRESS_EXACT",
        "geocoded_at": datetime.now(timezone.utc).isoformat(),
    }


def representative_transaction(rows):
    return sorted(rows, key=lambda row: (row.get("contract_year_month") or "", row.get("contract_day") or 0), reverse=True)[0]


def anchor_address(row):
    return " ".join(part for part in [row.get("sido"), row.get("sigungu"), row.get("dong"), row.get("jibun")] if part)


def geocode_anchors(args):
    load_env()
    transactions = read_jsonl(TRANSACTIONS_JSONL)
    grouped = defaultdict(list)
    for row in transactions:
        grouped[row["building_key"]].append(row)
    cache = read_json(GEOCODING_CACHE, {})
    keys = sorted(grouped.keys())
    geocoded = 0
    for index, key in enumerate(keys, start=1):
        if args.limit and geocoded >= args.limit:
            break
        if key in cache:
            continue
        rep = representative_transaction(grouped[key])
        query = anchor_address(rep)
        if not query:
            continue
        print(f"[{index}/{len(keys)}] geocode {query}")
        try:
            result = naver_geocode(query, timeout=args.timeout)
            cache[key] = result or {"quality": "FAILED", "geocoded_at": datetime.now(timezone.utc).isoformat()}
            geocoded += 1
            write_json(GEOCODING_CACHE, cache)
        except Exception as exc:
            cache[key] = {"quality": "FAILED", "error": str(exc), "geocoded_at": datetime.now(timezone.utc).isoformat()}
            write_json(GEOCODING_CACHE, cache)
            if args.fail_fast:
                raise
        time.sleep(args.sleep)
    print(f"geocoding cache entries: {len(cache)}")


def round_money(value, unit):
    rounded = (Decimal(str(value)) / unit).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * unit
    return int(rounded)


def price_from_transactions(rows, transaction_type):
    same = [row for row in rows if row["transaction_type"] == transaction_type]
    factor = Decimal(str(random.uniform(0.95, 1.10)))
    if transaction_type == "MONTHLY_RENT":
        deposits = [row["deposit"] for row in same if row.get("deposit")]
        rents = [row["monthly_rent"] for row in same if row.get("monthly_rent")]
        if not deposits or not rents:
            return None
        return {
            "deposit": round_money(Decimal(str(median(deposits))) * factor, Decimal("1000000")),
            "monthly_rent": round_money(Decimal(str(median(rents))) * factor, Decimal("10000")),
            "price": None,
        }
    if transaction_type == "JEONSE":
        deposits = [row["deposit"] for row in same if row.get("deposit")]
        if not deposits:
            return None
        return {"deposit": round_money(Decimal(str(median(deposits))) * factor, Decimal("1000000")), "monthly_rent": None, "price": None}
    prices = [row["price"] for row in same if row.get("price")]
    if not prices:
        return None
    return {"deposit": None, "monthly_rent": None, "price": round_money(Decimal(str(median(prices))) * factor, Decimal("10000000"))}


def generate_properties(args):
    random.seed(RANDOM_SEED)
    transactions = read_jsonl(TRANSACTIONS_JSONL)
    cache = read_json(GEOCODING_CACHE, {})
    grouped = defaultdict(list)
    for row in transactions:
        grouped[row["building_key"]].append(row)
    properties = []
    for building_key_value, rows in sorted(grouped.items()):
        coords = cache.get(building_key_value)
        if not coords or coords.get("quality") not in ("ADDRESS_EXACT", "BUILDING_EXACT"):
            continue
        rep = representative_transaction(rows)
        types = sorted({row["transaction_type"] for row in rows})
        random.shuffle(types)
        count = random.randint(args.min_per_anchor, args.max_per_anchor)
        for offset, transaction_type in enumerate(types[:count], start=1):
            price_fields = price_from_transactions(rows, transaction_type)
            if not price_fields:
                continue
            source_hash = hashlib.sha1(f"{building_key_value}:{transaction_type}:{offset}".encode("utf-8")).hexdigest()[:18]
            title_base = rep.get("building_name") or f"{rep['dong']} {rep['property_type']}"
            properties.append(
                {
                    "title": f"{title_base} 매물",
                    "building_name": rep.get("building_name"),
                    "building_key": building_key_value,
                    "anchor_transaction_key": rep["source_transaction_key"],
                    "property_type": rep["property_type"],
                    "transaction_type": transaction_type,
                    **price_fields,
                    "maintenance_fee": random.randint(5, 25) * 10000,
                    "area_m2": rep["area_m2"],
                    "floor": rep.get("floor"),
                    "total_floor": None,
                    "address": anchor_address(rep),
                    "road_address": rep.get("road_address"),
                    "sido": rep["sido"],
                    "sigungu": rep["sigungu"],
                    "dong": rep["dong"],
                    "legal_dong_code": rep["legal_dong_code"],
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"],
                    "geocoding_provider": coords.get("provider"),
                    "geocoding_quality": coords.get("quality"),
                    "geocoded_at": coords.get("geocoded_at"),
                    "description": "실거래가 건물 정보를 기준으로 생성한 MVP 더미 매물입니다.",
                    "source": "MVP_SYNTHETIC",
                    "source_property_id": f"synthetic-{source_hash}",
                    "source_url": None,
                    "crawled_at": None,
                    "registered_at": datetime.now(timezone.utc).date().isoformat(),
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            )
    ensure_dir(PROPERTIES_JSONL)
    PROPERTIES_JSONL.write_text("", encoding="utf-8")
    append_jsonl(PROPERTIES_JSONL, properties)
    print(f"generated properties: {len(properties)}")


def import_psycopg():
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise SystemExit("psycopg is required. Run: python -m pip install -r scripts/data_pipeline/requirements.txt") from exc
    return psycopg, dict_row


def db_conninfo():
    url = os.environ.get("SUPABASE_DB_URL")
    user = os.environ.get("SUPABASE_DB_USERNAME")
    password = os.environ.get("SUPABASE_DB_PASSWORD")
    if not url:
        raise SystemExit("SUPABASE_DB_URL is required.")
    if url.startswith("jdbc:postgresql://"):
        url = "postgresql://" + url.removeprefix("jdbc:postgresql://")
    parsed = parse.urlparse(url)
    if parsed.scheme not in ("postgresql", "postgres"):
        raise SystemExit("SUPABASE_DB_URL must be a PostgreSQL or JDBC PostgreSQL URL.")
    if parsed.username:
        return url
    if not user or not password:
        raise SystemExit("SUPABASE_DB_USERNAME and SUPABASE_DB_PASSWORD are required when URL has no credentials.")
    netloc = f"{parse.quote(user)}:{parse.quote(password)}@{parsed.netloc}"
    return parse.urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))


MIGRATION_TRACKING_SQL = """
create table if not exists public.schema_migrations (
    version varchar(255) primary key,
    applied_at timestamptz not null default now()
)
"""


def apply_migrations(args):
    load_env()
    psycopg, _ = import_psycopg()
    migrations_dir = args.migrations_dir
    migration_paths = sorted(migrations_dir.glob("*.sql"))
    if not migration_paths:
        raise SystemExit(f"No migration files found in {migrations_dir}")

    with psycopg.connect(db_conninfo(), prepare_threshold=None) as conn:
        with conn.cursor() as cur:
            cur.execute(MIGRATION_TRACKING_SQL)
            cur.execute("select version from public.schema_migrations")
            applied = {row[0] for row in cur.fetchall()}
            for migration_path in migration_paths:
                if migration_path.name in applied:
                    print(f"skipping migration: {migration_path.name}")
                    continue
                print(f"applying migration: {migration_path.name}")
                cur.execute(migration_path.read_text(encoding="utf-8"))
                cur.execute(
                    "insert into public.schema_migrations (version) values (%s) on conflict do nothing",
                    (migration_path.name,),
                )
        conn.commit()
    print(f"checked migrations: {len(migration_paths)}")


def execute_batch(cursor, sql, rows, page_size=1000):
    if not rows:
        return
    for start in range(0, len(rows), page_size):
        cursor.executemany(sql, rows[start : start + page_size])


def row_region_keys(row):
    legal_code = row["legal_dong_code"]
    dong_code = f"{legal_code}:{row['dong']}"
    return [
        ("SIDO", legal_code[:2], row["sido"], None, None),
        ("SIGUNGU", legal_code[:5], row["sido"], row["sigungu"], None),
        ("DONG", dong_code, row["sido"], row["sigungu"], row["dong"]),
    ]


def limited_related_rows(transactions, region_stats, building_stats, properties, limit):
    if not limit:
        return transactions, region_stats, building_stats, properties

    transactions = transactions[:limit]
    transaction_keys = {row["source_transaction_key"] for row in transactions}
    region_keys = {
        (level, code, row["property_type"], row["transaction_type"])
        for row in transactions
        for level, code, _sido, _sigungu, _dong in row_region_keys(row)
    }
    building_keys = {
        (row["building_key"], row["property_type"], row["transaction_type"])
        for row in transactions
    }
    return (
        transactions,
        [
            row
            for row in region_stats
            if (row["region_level"], row["region_code"], row["property_type"], row["transaction_type"]) in region_keys
        ],
        [
            row
            for row in building_stats
            if (row["building_key"], row["property_type"], row["transaction_type"]) in building_keys
        ],
        [row for row in properties if row.get("anchor_transaction_key") in transaction_keys],
    )


def load_supabase(args):
    load_env()
    psycopg, _ = import_psycopg()
    transactions = read_jsonl(TRANSACTIONS_JSONL)
    region_stats = read_jsonl(REGION_STATS_JSONL)
    building_stats = read_jsonl(BUILDING_STATS_JSONL)
    properties = read_jsonl(PROPERTIES_JSONL)
    transactions, region_stats, building_stats, properties = limited_related_rows(
        transactions,
        region_stats,
        building_stats,
        properties,
        args.limit,
    )

    with psycopg.connect(db_conninfo(), prepare_threshold=None) as conn:
        with conn.cursor() as cur:
            execute_batch(cur, TRANSACTION_UPSERT_SQL, [transaction_params(row) for row in transactions], args.batch_size)
            execute_batch(cur, REGION_STAT_UPSERT_SQL, [region_stat_params(row) for row in region_stats], args.batch_size)
            execute_batch(cur, BUILDING_STAT_UPSERT_SQL, [building_stat_params(row) for row in building_stats], args.batch_size)
            execute_batch(cur, PROPERTY_UPSERT_SQL, [property_params(row) for row in properties], args.batch_size)
        conn.commit()
    print(f"upserted transactions={len(transactions)} region_stats={len(region_stats)} building_stats={len(building_stats)} properties={len(properties)}")


TRANSACTION_COLUMNS = [
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


def transaction_params(row):
    return tuple(json.dumps(row.get(column), ensure_ascii=False) if column == "raw_json" else row.get(column) for column in TRANSACTION_COLUMNS)


TRANSACTION_UPSERT_SQL = """
insert into public.transaction_history (
    source_api, source_transaction_key, property_type, transaction_type, sido, sigungu, dong,
    legal_dong_code, jibun, building_name, building_key, contract_year_month, contract_day,
    deposit, monthly_rent, price, area_m2, floor, build_year, raw_json
) values (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb
)
on conflict (source_api, source_transaction_key) do update set
    property_type = excluded.property_type,
    transaction_type = excluded.transaction_type,
    sido = excluded.sido,
    sigungu = excluded.sigungu,
    dong = excluded.dong,
    legal_dong_code = excluded.legal_dong_code,
    jibun = excluded.jibun,
    building_name = excluded.building_name,
    building_key = excluded.building_key,
    contract_year_month = excluded.contract_year_month,
    contract_day = excluded.contract_day,
    deposit = excluded.deposit,
    monthly_rent = excluded.monthly_rent,
    price = excluded.price,
    area_m2 = excluded.area_m2,
    floor = excluded.floor,
    build_year = excluded.build_year,
    raw_json = excluded.raw_json
"""


STAT_COLUMNS = [
    "avg_deposit",
    "median_deposit",
    "avg_monthly_rent",
    "median_monthly_rent",
    "avg_price",
    "median_price",
    "transaction_count",
    "sample_from_ym",
    "sample_to_ym",
]


def region_stat_params(row):
    return (
        row.get("region_level"),
        row.get("region_code"),
        row.get("sido"),
        row.get("sigungu"),
        row.get("dong"),
        row.get("property_type"),
        row.get("transaction_type"),
        *(row.get(column) for column in STAT_COLUMNS),
    )


REGION_STAT_UPSERT_SQL = """
insert into public.region_price_stat (
    region_level, region_code, sido, sigungu, dong, property_type, transaction_type,
    avg_deposit, median_deposit, avg_monthly_rent, median_monthly_rent,
    avg_price, median_price, transaction_count, sample_from_ym, sample_to_ym
) values (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
on conflict (region_level, region_code, property_type, transaction_type) do update set
    sido = excluded.sido,
    sigungu = excluded.sigungu,
    dong = excluded.dong,
    avg_deposit = excluded.avg_deposit,
    median_deposit = excluded.median_deposit,
    avg_monthly_rent = excluded.avg_monthly_rent,
    median_monthly_rent = excluded.median_monthly_rent,
    avg_price = excluded.avg_price,
    median_price = excluded.median_price,
    transaction_count = excluded.transaction_count,
    sample_from_ym = excluded.sample_from_ym,
    sample_to_ym = excluded.sample_to_ym,
    updated_at = now()
"""


def building_stat_params(row):
    return (
        row.get("building_key"),
        row.get("building_name"),
        row.get("sido"),
        row.get("sigungu"),
        row.get("dong"),
        row.get("legal_dong_code"),
        row.get("property_type"),
        row.get("transaction_type"),
        *(row.get(column) for column in STAT_COLUMNS),
    )


BUILDING_STAT_UPSERT_SQL = """
insert into public.building_price_stat (
    building_key, building_name, sido, sigungu, dong, legal_dong_code, property_type, transaction_type,
    avg_deposit, median_deposit, avg_monthly_rent, median_monthly_rent,
    avg_price, median_price, transaction_count, sample_from_ym, sample_to_ym
) values (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
on conflict (building_key, property_type, transaction_type) do update set
    building_name = excluded.building_name,
    sido = excluded.sido,
    sigungu = excluded.sigungu,
    dong = excluded.dong,
    legal_dong_code = excluded.legal_dong_code,
    avg_deposit = excluded.avg_deposit,
    median_deposit = excluded.median_deposit,
    avg_monthly_rent = excluded.avg_monthly_rent,
    median_monthly_rent = excluded.median_monthly_rent,
    avg_price = excluded.avg_price,
    median_price = excluded.median_price,
    transaction_count = excluded.transaction_count,
    sample_from_ym = excluded.sample_from_ym,
    sample_to_ym = excluded.sample_to_ym,
    updated_at = now()
"""


PROPERTY_COLUMNS = [
    "title",
    "building_name",
    "building_key",
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


def property_params(row):
    return (row.get("anchor_transaction_key"), *(row.get(column) for column in PROPERTY_COLUMNS))


PROPERTY_UPSERT_SQL = """
insert into public.properties (
    anchor_transaction_id, title, building_name, building_key, property_type, transaction_type,
    deposit, monthly_rent, price, maintenance_fee, area_m2, floor, total_floor, address,
    road_address, sido, sigungu, dong, legal_dong_code, latitude, longitude,
    geocoding_provider, geocoding_quality, geocoded_at, description, source, source_property_id,
    source_url, crawled_at, registered_at, is_active, created_at, updated_at
) values (
    (select id from public.transaction_history where source_transaction_key = %s limit 1),
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
on conflict (source, source_property_id) do update set
    title = excluded.title,
    building_name = excluded.building_name,
    building_key = excluded.building_key,
    anchor_transaction_id = excluded.anchor_transaction_id,
    property_type = excluded.property_type,
    transaction_type = excluded.transaction_type,
    deposit = excluded.deposit,
    monthly_rent = excluded.monthly_rent,
    price = excluded.price,
    maintenance_fee = excluded.maintenance_fee,
    area_m2 = excluded.area_m2,
    floor = excluded.floor,
    total_floor = excluded.total_floor,
    address = excluded.address,
    road_address = excluded.road_address,
    sido = excluded.sido,
    sigungu = excluded.sigungu,
    dong = excluded.dong,
    legal_dong_code = excluded.legal_dong_code,
    latitude = excluded.latitude,
    longitude = excluded.longitude,
    geocoding_provider = excluded.geocoding_provider,
    geocoding_quality = excluded.geocoding_quality,
    geocoded_at = excluded.geocoded_at,
    description = excluded.description,
    source_url = excluded.source_url,
    crawled_at = excluded.crawled_at,
    registered_at = excluded.registered_at,
    is_active = excluded.is_active,
    updated_at = excluded.updated_at
"""


def verify_db():
    load_env()
    psycopg, dict_row = import_psycopg()
    queries = {
        "transaction_history": "select count(*) as count from public.transaction_history",
        "properties": "select count(*) as count from public.properties",
        "properties_missing_coords": "select count(*) as count from public.properties where latitude is null or longitude is null",
        "region_price_stat": "select count(*) as count from public.region_price_stat",
        "building_price_stat": "select count(*) as count from public.building_price_stat",
    }
    with psycopg.connect(db_conninfo(), row_factory=dict_row, prepare_threshold=None) as conn:
        with conn.cursor() as cur:
            for label, sql in queries.items():
                cur.execute(sql)
                print(f"{label}: {cur.fetchone()['count']}")


def run_pipeline(args):
    if args.migrate_db:
        apply_migrations(args)
    fetch_transactions(args)
    normalize_manifest()
    compute_stats()
    geocode_anchors(args)
    generate_properties(args)
    if args.load_db:
        load_supabase(args)
        verify_db()


def add_common_args(parser):
    parser.add_argument("--lawd-codes", type=Path, default=DEFAULT_LAWD_CODES)
    parser.add_argument("--scope", choices=["nationwide"], default="nationwide")
    parser.add_argument("--months", type=int, default=12)
    parser.add_argument("--month-values", help="Comma-separated YYYYMM values. Overrides --months.")
    parser.add_argument("--source-apis", help="Comma-separated source API names.")
    parser.add_argument("--limit-regions", type=int)
    parser.add_argument("--limit-requests", type=int)
    parser.add_argument("--num-of-rows", type=int, default=1000)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--sleep", type=float, default=0.15)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--min-per-anchor", type=int, default=1)
    parser.add_argument("--max-per-anchor", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--load-db", action="store_true")
    parser.add_argument("--migrate-db", action="store_true")
    parser.add_argument("--migrations-dir", type=Path, default=MIGRATIONS_DIR)


def command_plan(args):
    regions = load_lawd_codes(args.lawd_codes)
    months = parse_csv_list(args.month_values) or recent_months(args.months)
    source_apis = selected_source_apis(args.source_apis)
    requests_to_run = planned_requests(regions, months, source_apis, args.limit_regions, args.limit_requests)
    print(f"regions: {len(regions)}")
    print(f"months: {len(months)} ({months[-1]}..{months[0]})")
    print(f"source APIs: {len(source_apis)}")
    print(f"planned requests before pagination: {len(requests_to_run)}")
    if requests_to_run:
        source_api, region, month = requests_to_run[0]
        print(f"first: {source_api} {region['lawdCd']} {region['sido']} {region['sigungu']} {month}")


def parse_args():
    parser = argparse.ArgumentParser(description="Build and load the offline nationwide real-estate MVP dataset.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ["plan", "fetch", "normalize", "compute-stats", "geocode", "generate-properties", "migrate-db", "load-db", "verify-db", "run"]:
        sub = subparsers.add_parser(command)
        add_common_args(sub)
    args = parser.parse_args()
    if args.min_per_anchor > args.max_per_anchor:
        parser.error("--min-per-anchor must be less than or equal to --max-per-anchor")
    return args


def main():
    args = parse_args()
    if args.command == "plan":
        command_plan(args)
    elif args.command == "fetch":
        fetch_transactions(args)
    elif args.command == "normalize":
        normalize_manifest()
    elif args.command == "compute-stats":
        compute_stats()
    elif args.command == "geocode":
        load_env()
        geocode_anchors(args)
    elif args.command == "generate-properties":
        generate_properties(args)
    elif args.command == "migrate-db":
        apply_migrations(args)
    elif args.command == "load-db":
        if args.migrate_db:
            apply_migrations(args)
        load_supabase(args)
    elif args.command == "verify-db":
        verify_db()
    elif args.command == "run":
        run_pipeline(args)


if __name__ == "__main__":
    main()
