import argparse
import json
import os
from pathlib import Path
from urllib import error, parse, request


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "molit"
DEFAULT_PLAN_PATH = RAW_DIR / "fetch-plan.json"
DEFAULT_MANIFEST_PATH = RAW_DIR / "manifest.json"

SOURCE_CONFIG = {
    "MOLIT_APT_RENT": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent",
        "file_prefix": "apt-rent",
    },
    "MOLIT_OFFICETEL_RENT": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcOffiRent/getRTMSDataSvcOffiRent",
        "file_prefix": "officetel-rent",
    },
    "MOLIT_VILLA_RENT": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcRHRent/getRTMSDataSvcRHRent",
        "file_prefix": "villa-rent",
    },
    "MOLIT_MULTI_FAMILY_RENT": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent",
        "file_prefix": "multi-family-rent",
    },
    "MOLIT_APT_SALE": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev",
        "file_prefix": "apt-sale",
    },
    "MOLIT_OFFICETEL_SALE": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcOffiTrade/getRTMSDataSvcOffiTrade",
        "file_prefix": "officetel-sale",
    },
    "MOLIT_VILLA_SALE": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade",
        "file_prefix": "villa-sale",
    },
    "MOLIT_MULTI_FAMILY_SALE": {
        "url": "https://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade",
        "file_prefix": "multi-family-sale",
    },
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


def load_local_env():
    load_env_file(ROOT / ".env.local")
    load_env_file(ROOT / ".env")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def service_key_param(service_key):
    if "%" in service_key:
        return service_key
    return parse.quote(service_key, safe="")


def build_url(base_url, service_key, lawd_cd, deal_ymd, num_of_rows, page_no):
    query = parse.urlencode(
        {
            "LAWD_CD": lawd_cd,
            "DEAL_YMD": deal_ymd,
            "numOfRows": num_of_rows,
            "pageNo": page_no,
        }
    )
    return f"{base_url}?serviceKey={service_key_param(service_key)}&{query}"


def fetch_xml(url, timeout=30):
    req = request.Request(url, headers={"Accept": "application/xml"})
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"MOLIT request failed ({exc.code}): {message}") from exc


def planned_requests(plan, source_filter=None, region_filter=None, month_filter=None):
    months = month_filter or plan["months"]
    source_apis = source_filter or plan["sourceApis"]
    regions = plan["regions"]
    if region_filter:
        wanted = set(region_filter)
        regions = [region for region in regions if region["lawdCd"] in wanted]

    for source_api in source_apis:
        if source_api not in SOURCE_CONFIG:
            raise ValueError(f"Unsupported sourceApi: {source_api}")
        for region in regions:
            for month in months:
                config = SOURCE_CONFIG[source_api]
                filename = f"{config['file_prefix']}-{region['lawdCd']}-{month}.xml"
                yield {
                    "sourceApi": source_api,
                    "url": config["url"],
                    "filename": filename,
                    "month": month,
                    "region": region,
                }


def fetch_plan(plan, service_key, output_dir, num_of_rows, page_no, dry_run=False, source_filter=None, region_filter=None, month_filter=None):
    manifest_entries = []
    requests = list(planned_requests(plan, source_filter=source_filter, region_filter=region_filter, month_filter=month_filter))
    for item in requests:
        region = item["region"]
        xml_path = output_dir / item["filename"]
        url = build_url(item["url"], service_key, region["lawdCd"], item["month"], num_of_rows, page_no)
        if not dry_run:
            xml = fetch_xml(url)
            xml_path.write_text(xml, encoding="utf-8")
        manifest_entries.append(
            {
                "sourceApi": item["sourceApi"],
                "xmlPath": item["filename"],
                "sido": region["sido"],
                "sigungu": region["sigungu"],
                "legalDongCodePrefix": region["lawdCd"],
                "dealYmd": item["month"],
            }
        )
    return manifest_entries


def parse_csv(values):
    if not values:
        return None
    return [value.strip() for value in values.split(",") if value.strip()]


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch MOLIT real-transaction XML responses for local F-1 seeds.")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--output-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--num-of-rows", type=int, default=1000)
    parser.add_argument("--page-no", type=int, default=1)
    parser.add_argument("--source-apis", help="Comma-separated sourceApi filter")
    parser.add_argument("--regions", help="Comma-separated LAWD_CD filter")
    parser.add_argument("--months", help="Comma-separated DEAL_YMD filter")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    load_local_env()
    service_key = os.environ.get("MOLIT_SERVICE_KEY")
    if not service_key:
        raise SystemExit("MOLIT_SERVICE_KEY is required.")
    if not args.plan.exists():
        raise SystemExit(f"Fetch plan not found: {args.plan}")

    plan = read_json(args.plan)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_entries = fetch_plan(
        plan,
        service_key,
        args.output_dir,
        args.num_of_rows,
        args.page_no,
        dry_run=args.dry_run,
        source_filter=parse_csv(args.source_apis),
        region_filter=parse_csv(args.regions),
        month_filter=parse_csv(args.months),
    )

    if not args.dry_run:
        write_json(args.manifest, {"files": manifest_entries})

    print(f"planned {len(manifest_entries)} MOLIT requests")
    print(args.manifest)


if __name__ == "__main__":
    main()
