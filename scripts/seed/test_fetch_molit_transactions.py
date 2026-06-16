import unittest

import fetch_molit_transactions as fetcher


class FetchMolitTransactionsTest(unittest.TestCase):
    def test_build_url_keeps_encoded_service_key(self):
        url = fetcher.build_url(
            "https://example.test/api",
            "abc%2Fdef%3D%3D",
            "11680",
            "202606",
            100,
            1,
        )

        self.assertIn("serviceKey=abc%2Fdef%3D%3D", url)
        self.assertIn("LAWD_CD=11680", url)
        self.assertIn("DEAL_YMD=202606", url)

    def test_planned_requests_cross_joins_sources_regions_months(self):
        plan = {
            "months": ["202605", "202606"],
            "sourceApis": ["MOLIT_APT_RENT", "MOLIT_APT_SALE"],
            "regions": [
                {"sido": "서울특별시", "sigungu": "강남구", "lawdCd": "11680"},
                {"sido": "서울특별시", "sigungu": "관악구", "lawdCd": "11620"},
            ],
        }

        requests = list(fetcher.planned_requests(plan))

        self.assertEqual(len(requests), 8)
        self.assertEqual(requests[0]["filename"], "apt-rent-11680-202605.xml")
        self.assertEqual(requests[-1]["filename"], "apt-sale-11620-202606.xml")

    def test_fetch_plan_continues_after_failure(self):
        plan = {
            "months": ["202606"],
            "sourceApis": ["MOLIT_APT_RENT"],
            "regions": [
                {"sido": "서울특별시", "sigungu": "강남구", "lawdCd": "11680"},
            ],
        }
        original = fetcher.fetch_xml_with_retries

        def failing_fetch(url, timeout, retries, retry_sleep):
            raise RuntimeError("timeout")

        try:
            fetcher.fetch_xml_with_retries = failing_fetch
            manifest_entries, errors = fetcher.fetch_plan(
                plan,
                "service-key",
                output_dir=__import__("pathlib").Path("."),
                num_of_rows=100,
                page_no=1,
                retries=0,
                quiet=True,
            )
        finally:
            fetcher.fetch_xml_with_retries = original

        self.assertEqual(manifest_entries, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("timeout", errors[0]["error"])


if __name__ == "__main__":
    unittest.main()
