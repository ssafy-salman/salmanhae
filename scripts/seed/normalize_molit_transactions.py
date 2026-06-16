import argparse
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = ROOT / "data" / "raw" / "molit" / "manifest.json"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "seed" / "transaction-history.seed.json"

SOURCE_CONFIG = {
    "MOLIT_APT_RENT": {"property_type": "APARTMENT", "mode": "RENT"},
    "MOLIT_OFFICETEL_RENT": {"property_type": "OFFICETEL", "mode": "RENT"},
    "MOLIT_VILLA_RENT": {"property_type": "VILLA", "mode": "RENT"},
    "MOLIT_MULTI_FAMILY_RENT": {"property_type": "MULTI_FAMILY", "mode": "RENT"},
    "MOLIT_APT_SALE": {"property_type": "APARTMENT", "mode": "SALE"},
    "MOLIT_OFFICETEL_SALE": {"property_type": "OFFICETEL", "mode": "SALE"},
    "MOLIT_VILLA_SALE": {"property_type": "VILLA", "mode": "SALE"},
    "MOLIT_MULTI_FAMILY_SALE": {"property_type": "MULTI_FAMILY", "mode": "SALE"},
}

ALIASES = {
    "dong": ["umdNm", "법정동", "dong", "법정동명"],
    "umd_code": ["umdCd", "법정동읍면동코드", "umdCode"],
    "jibun": ["jibun", "지번", "본번", "bonbun"],
    "building_name": [
        "aptNm",
        "아파트",
        "단지명",
        "offiNm",
        "오피스텔",
        "mhouseNm",
        "연립다세대",
        "houseNm",
        "주택명",
    ],
    "area_m2": ["excluUseAr", "전용면적", "area", "계약면적"],
    "floor": ["floor", "층"],
    "build_year": ["buildYear", "건축년도", "건축연도"],
    "deal_year": ["dealYear", "년", "contractYear"],
    "deal_month": ["dealMonth", "월", "contractMonth"],
    "deal_day": ["dealDay", "일", "contractDay"],
    "contract_year_month": ["contractYearMonth", "계약년월", "dealYearMonth"],
    "deposit": ["deposit", "보증금액", "보증금", "rentDeposit"],
    "monthly_rent": ["monthlyRent", "월세금액", "월세", "rentFee"],
    "price": ["dealAmount", "거래금액", "dealAmt", "price"],
    "legal_dong_code": ["legalDongCode", "법정동코드"],
}


def strip_namespace(tag):
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def item_elements(root):
    return [element for element in root.iter() if strip_namespace(element.tag) == "item"]


def item_to_dict(element):
    result = {}
    for child in list(element):
        key = strip_namespace(child.tag)
        value = (child.text or "").strip()
        result[key] = value
    return result


def first_value(row, field):
    for key in ALIASES[field]:
        value = row.get(key)
        if value not in (None, ""):
            return value.strip() if isinstance(value, str) else value
    return None


def digits(value):
    if value is None:
        return None
    found = re.findall(r"\d+", str(value).replace(",", ""))
    return "".join(found) if found else None


def parse_decimal(value):
    if value in (None, ""):
        return None
    cleaned = str(value).replace(",", "").replace("㎡", "").strip()
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


def contract_parts(row):
    year_month = first_value(row, "contract_year_month")
    if year_month:
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
    direct = digits(first_value(row, "legal_dong_code"))
    if direct:
        return direct[:10]

    prefix = digits(manifest_entry.get("legalDongCodePrefix") or manifest_entry.get("lawdCd"))
    umd_code = digits(first_value(row, "umd_code"))
    if prefix and umd_code:
        return f"{prefix[:5]}{umd_code[-5:]}"[:10]
    return prefix[:10] if prefix else None


def building_key(row, normalized):
    parts = [
        normalized["legal_dong_code"],
        normalized["property_type"],
        normalized.get("building_name"),
        normalized.get("jibun"),
    ]
    return ":".join(part for part in parts if part)


def source_transaction_key(normalized):
    key_fields = [
        normalized["source_api"],
        normalized["legal_dong_code"],
        normalized["dong"],
        normalized.get("jibun"),
        normalized.get("building_name"),
        normalized["contract_year_month"],
        normalized.get("contract_day"),
        normalized["property_type"],
        normalized["transaction_type"],
        normalized.get("area_m2"),
        normalized.get("floor"),
        normalized.get("deposit"),
        normalized.get("monthly_rent"),
        normalized.get("price"),
    ]
    raw_key = "|".join("" if value is None else str(value) for value in key_fields)
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
        "dong": first_value(row, "dong") or manifest_entry.get("dong"),
        "legal_dong_code": legal_dong_code(row, manifest_entry),
        "jibun": first_value(row, "jibun"),
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
        deposit = parse_money_won(first_value(row, "deposit"))
        monthly_rent = parse_money_won(first_value(row, "monthly_rent"))
        normalized["deposit"] = deposit
        normalized["monthly_rent"] = monthly_rent if monthly_rent and monthly_rent > 0 else None
        normalized["transaction_type"] = "MONTHLY_RENT" if normalized["monthly_rent"] else "JEONSE"
    else:
        normalized["price"] = parse_money_won(first_value(row, "price"))

    required = [
        "property_type",
        "transaction_type",
        "sido",
        "sigungu",
        "dong",
        "legal_dong_code",
        "contract_year_month",
        "area_m2",
    ]
    if any(normalized.get(field) in (None, "") for field in required):
        return None

    if normalized["transaction_type"] == "SALE" and not normalized["price"]:
        return None
    if normalized["transaction_type"] == "JEONSE" and not normalized["deposit"]:
        return None
    if normalized["transaction_type"] == "MONTHLY_RENT" and (
        not normalized["deposit"] or not normalized["monthly_rent"]
    ):
        return None

    normalized["building_key"] = building_key(row, normalized)
    normalized["source_transaction_key"] = source_transaction_key(normalized)
    return normalized


def normalize_xml_file(path, manifest_entry):
    root = ElementTree.parse(path).getroot()
    rows = []
    for item in item_elements(root):
        normalized = normalize_row(item_to_dict(item), manifest_entry)
        if normalized:
            rows.append(normalized)
    return rows


def read_manifest(path):
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("files", [])


def normalize_manifest(manifest_path):
    entries = read_manifest(manifest_path)
    output = []
    base_dir = manifest_path.parent
    for entry in entries:
        source_api = entry.get("sourceApi")
        if source_api not in SOURCE_CONFIG:
            raise ValueError(f"Unsupported sourceApi: {source_api}")
        xml_path = Path(entry["xmlPath"])
        if not xml_path.is_absolute():
            xml_path = base_dir / xml_path
        output.extend(normalize_xml_file(xml_path, entry))
    return sorted(output, key=lambda row: row["source_transaction_key"])


def write_output(rows, output_path):
    payload = {
        "schemaVersion": 1,
        "source": "MOLIT_REAL_TRANSACTION_NORMALIZED",
        "totalCount": len(rows),
        "items": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Normalize MOLIT real-transaction XML files for F-1 seeds.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def main():
    args = parse_args()
    rows = normalize_manifest(args.manifest)
    write_output(rows, args.output)
    print(f"normalized {len(rows)} transaction rows")
    print(args.output)


if __name__ == "__main__":
    main()
