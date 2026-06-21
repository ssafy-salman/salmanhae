import tempfile
import unittest
from pathlib import Path

import normalize_molit_transactions as normalizer


class NormalizeMolitTransactionsTest(unittest.TestCase):
    def test_normalizes_apt_rent_xml_to_jeonse_row(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <body>
    <items>
      <item>
        <aptNm>도곡렉슬</aptNm>
        <umdNm>도곡동</umdNm>
        <umdCd>11800</umdCd>
        <jibun>527</jibun>
        <excluUseAr>84.99</excluUseAr>
        <floor>10</floor>
        <dealYear>2026</dealYear>
        <dealMonth>5</dealMonth>
        <dealDay>12</dealDay>
        <deposit>90,000</deposit>
        <monthlyRent>0</monthlyRent>
        <buildYear>2006</buildYear>
      </item>
    </items>
  </body>
</response>
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            xml_path = Path(temp_dir) / "apt-rent.xml"
            xml_path.write_text(xml, encoding="utf-8")

            rows = normalizer.normalize_xml_file(
                xml_path,
                {
                    "sourceApi": "MOLIT_APT_RENT",
                    "sido": "서울특별시",
                    "sigungu": "강남구",
                    "legalDongCodePrefix": "11680",
                },
            )

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["property_type"], "APARTMENT")
        self.assertEqual(row["transaction_type"], "JEONSE")
        self.assertEqual(row["building_name"], "도곡렉슬")
        self.assertEqual(row["legal_dong_code"], "1168011800")
        self.assertEqual(row["deposit"], 900000000)
        self.assertIsNone(row["monthly_rent"])
        self.assertEqual(row["area_m2"], 84.99)
        self.assertEqual(row["building_key"], "1168011800:APARTMENT:도곡렉슬:527")

    def test_normalizes_apt_sale_xml_to_sale_row(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<response><body><items><item>
  <aptNm>도곡렉슬</aptNm>
  <umdNm>도곡동</umdNm>
  <jibun>527</jibun>
  <excluUseAr>84.99</excluUseAr>
  <floor>11</floor>
  <dealYear>2026</dealYear>
  <dealMonth>6</dealMonth>
  <dealDay>2</dealDay>
  <dealAmount>250,000</dealAmount>
  <buildYear>2006</buildYear>
</item></items></body></response>
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            xml_path = Path(temp_dir) / "apt-sale.xml"
            xml_path.write_text(xml, encoding="utf-8")

            rows = normalizer.normalize_xml_file(
                xml_path,
                {
                    "sourceApi": "MOLIT_APT_SALE",
                    "sido": "서울특별시",
                    "sigungu": "강남구",
                    "legalDongCodePrefix": "11680",
                    "dong": "도곡동",
                },
            )

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["transaction_type"], "SALE")
        self.assertEqual(row["price"], 2500000000)
        self.assertIsNone(row["deposit"])
        self.assertEqual(row["contract_year_month"], "202606")


if __name__ == "__main__":
    unittest.main()
