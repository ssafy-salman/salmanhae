import argparse
import json
import os
import time
from pathlib import Path
from urllib import error, parse, request


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "molit"
DEFAULT_PLAN_PATH = RAW_DIR / "fetch-plan.json"
DEFAULT_MANIFEST_PATH = RAW_DIR / "manifest.json"
DEFAULT_ERRORS_PATH = RAW_DIR / "fetch-errors.json"

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
    params = {
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": deal_ymd,
    }
    if num_of_rows is not None:
        params["numOfRows"] = num_of_rows
    if page_no is not None:
        params["pageNo"] = page_no
    query = parse.urlencode(params)
    return f"{base_url}?serviceKey={service_key_param(service_key)}&{query}"


def fetch_xml(url, timeout=60):
    req = request.Request(url, headers={"Accept": "application/xml"})
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"MOLIT request failed ({exc.code}): {message}") from exc
    except (TimeoutError, error.URLError) as exc:
        raise RuntimeError(f"MOLIT request failed: {exc}") from exc


def fetch_xml_with_retries(url, timeout, retries, retry_sleep):
    last_error = None
    for attempt in range(1, retries + 2):
        try:
            return fetch_xml(url, timeout=timeout)
        except RuntimeError as exc:
            last_error = exc
            if attempt > retries:
                break
            print(f"  retry {attempt}/{retries}: {exc}")
            time.sleep(retry_sleep)
    raise last_error


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


def manifest_entry(item):
    region = item["region"]
    return {
        "sourceApi": item["sourceApi"],
        "xmlPath": item["filename"],
        "sido": region["sido"],
        "sigungu": region["sigungu"],
        "legalDongCodePrefix": region["lawdCd"],
        "dealYmd": item["month"],
    }


def fetch_plan(
    plan,
    service_key,
    output_dir,
    num_of_rows,
    page_no,
    dry_run=False,
    source_filter=None,
    region_filter=None,
    month_filter=None,
    timeout=60,
    retries=2,
    retry_sleep=2,
    skip_existing=True,
    fail_fast=False,
    limit=None,
    quiet=False,
):
    manifest_entries = []
    errors = []
    requests = list(planned_requests(plan, source_filter=source_filter, region_filter=region_filter, month_filter=month_filter))
    if limit is not None:
        requests = requests[:limit]

    for index, item in enumerate(requests, start=1):
        region = item["region"]
        xml_path = output_dir / item["filename"]
        url = build_url(item["url"], service_key, region["lawdCd"], item["month"], num_of_rows, page_no)
        if not quiet:
            print(f"[{index}/{len(requests)}] {item['sourceApi']} {region['lawdCd']} {item['month']} -> {item['filename']}")

        entry = manifest_entry(item)
        if dry_run:
            manifest_entries.append(entry)
            continue

        if skip_existing and xml_path.exists() and xml_path.stat().st_size > 0:
            if not quiet:
                print("  skip existing")
            manifest_entries.append(entry)
            continue

        try:
            xml = fetch_xml_with_retries(url, timeout=timeout, retries=retries, retry_sleep=retry_sleep)
            xml_path.write_text(xml, encoding="utf-8")
            manifest_entries.append(entry)
        except RuntimeError as exc:
            error_entry = {
                "sourceApi": item["sourceApi"],
                "xmlPath": item["filename"],
                "sido": region["sido"],
                "sigungu": region["sigungu"],
                "legalDongCodePrefix": region["lawdCd"],
                "dealYmd": item["month"],
                "error": str(exc),
            }
            errors.append(error_entry)
            if not quiet:
                print(f"  failed: {exc}")
            if fail_fast:
                raise
    return manifest_entries, errors


def parse_csv(values):
    if not values:
        return None
    return [value.strip() for value in values.split(",") if value.strip()]


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch MOLIT real-transaction XML responses for local F-1 seeds.")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--output-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--num-of-rows", type=int)
    parser.add_argument("--page-no", type=int)
    parser.add_argument("--source-apis", help="Comma-separated sourceApi filter")
    parser.add_argument("--regions", help="Comma-separated LAWD_CD filter")
    parser.add_argument("--months", help="Comma-separated DEAL_YMD filter")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--retry-sleep", type=float, default=2)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
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
    manifest_entries, errors = fetch_plan(
        plan,
        service_key,
        args.output_dir,
        args.num_of_rows,
        args.page_no,
        dry_run=args.dry_run,
        source_filter=parse_csv(args.source_apis),
        region_filter=parse_csv(args.regions),
        month_filter=parse_csv(args.months),
        timeout=args.timeout,
        retries=args.retries,
        retry_sleep=args.retry_sleep,
        skip_existing=not args.no_skip_existing,
        fail_fast=args.fail_fast,
        limit=args.limit,
        quiet=False,
    )

    if not args.dry_run:
        write_json(args.manifest, {"files": manifest_entries})
        if errors:
            write_json(DEFAULT_ERRORS_PATH, {"errors": errors})

    print(f"successful {len(manifest_entries)} MOLIT requests")
    print(f"failed {len(errors)} MOLIT requests")
    print(args.manifest)


if __name__ == "__main__":
    main()
