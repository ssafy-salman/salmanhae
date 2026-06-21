import unittest

import geocode_property_anchors as geocoder


class GeocodePropertyAnchorsTest(unittest.TestCase):
    def test_collects_building_and_address_queries(self):
        rows = [
            {
                "building_key": "1168011800:APARTMENT:도곡렉슬:527",
                "sido": "서울특별시",
                "sigungu": "강남구",
                "dong": "도곡동",
                "building_name": "도곡렉슬",
                "jibun": "527",
            }
        ]

        anchors = geocoder.collect_anchors(rows)

        self.assertEqual(list(anchors), ["1168011800:APARTMENT:도곡렉슬:527"])
        queries = anchors["1168011800:APARTMENT:도곡렉슬:527"]["queries"]
        self.assertEqual(queries[0], {"query": "서울특별시 강남구 도곡동 도곡렉슬", "quality": "BUILDING_EXACT"})
        self.assertEqual(queries[1], {"query": "서울특별시 강남구 도곡동 527", "quality": "ADDRESS_EXACT"})

    def test_updates_cache_with_mocked_geocoder(self):
        rows = [
            {
                "building_key": "1168011800:APARTMENT:도곡렉슬:527",
                "sido": "서울특별시",
                "sigungu": "강남구",
                "dong": "도곡동",
                "building_name": "도곡렉슬",
                "jibun": "527",
            }
        ]
        original = geocoder.geocode_anchor

        def fake_geocode(anchor, client_id, client_secret):
            return {
                "latitude": 37.4935415,
                "longitude": 127.0505473,
                "provider": "NAVER",
                "quality": "BUILDING_EXACT",
                "query": anchor["queries"][0]["query"],
                "geocoded_at": "2026-06-16T00:00:00+00:00",
            }

        try:
            geocoder.geocode_anchor = fake_geocode
            cache = {}
            results = geocoder.update_cache(rows, cache, "id", "secret", sleep_seconds=0)
        finally:
            geocoder.geocode_anchor = original

        self.assertEqual(len(results), 1)
        self.assertEqual(cache["1168011800:APARTMENT:도곡렉슬:527"]["quality"], "BUILDING_EXACT")
        self.assertEqual(cache["1168011800:APARTMENT:도곡렉슬:527"]["latitude"], 37.4935415)


if __name__ == "__main__":
    unittest.main()
