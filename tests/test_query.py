import unittest
from datetime import date

from ai4eo.rag.query import FilterError, Filters, parse_filters

REGIONS = ["Assam", "Bihar", "Kerala"]
TYPES = ["bulletin", "report"]


def parse(raw):
    return parse_filters(raw, allowed_regions=REGIONS, allowed_doc_types=TYPES)


class ParseFilterTests(unittest.TestCase):
    def test_valid_filters(self):
        f = parse(
            {
                "region": "assam",
                "date_from": "2024-07-01",
                "date_to": "2024-07-31",
                "doc_types": ["bulletin"],
            }
        )
        self.assertEqual(f.region, "Assam")  # canonical spelling
        self.assertEqual(f.date_from, date(2024, 7, 1))
        self.assertEqual(f.doc_types, ("bulletin",))

    def test_nulls_and_empty(self):
        self.assertEqual(parse({}), Filters())
        self.assertEqual(parse({"region": None, "doc_types": None}), Filters())

    def test_unknown_key_rejected(self):
        with self.assertRaises(FilterError):
            parse({"region": "Assam", "sql": "DROP TABLE x"})

    def test_region_outside_allowed_list_rejected(self):
        with self.assertRaises(FilterError):
            parse({"region": "Atlantis"})

    def test_bad_dates_rejected(self):
        for bad in ("July 2024", 20240701, "2024-13-40"):
            with self.assertRaises(FilterError):
                parse({"date_from": bad})
        with self.assertRaises(FilterError):
            parse({"date_from": "2024-08-01", "date_to": "2024-07-01"})

    def test_doc_types_checked(self):
        with self.assertRaises(FilterError):
            parse({"doc_types": ["rumour"]})
        with self.assertRaises(FilterError):
            parse({"doc_types": "bulletin"})

    def test_filters_apply_to_metadata(self):
        f = parse({"region": "Assam", "date_from": "2024-07-01"})
        self.assertTrue(f.matches({"region": "Assam", "published": "2024-07-05"}))
        self.assertFalse(f.matches({"region": "Bihar", "published": "2024-07-05"}))
        self.assertFalse(f.matches({"region": "Assam", "published": "2024-06-30"}))


if __name__ == "__main__":
    unittest.main()
