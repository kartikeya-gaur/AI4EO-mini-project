import unittest
from datetime import date

from ai4eo.rag.filters import matches_filters

META = {"region": "Assam", "doc_type": "bulletin", "published": "2024-07-05"}


class FilterTests(unittest.TestCase):
    def test_no_filters_matches(self):
        self.assertTrue(matches_filters({}))

    def test_region_case_insensitive(self):
        self.assertTrue(matches_filters(META, region="assam"))
        self.assertFalse(matches_filters(META, region="Bihar"))

    def test_missing_region_excluded_when_filtering(self):
        self.assertFalse(matches_filters({"published": "2024-07-05"}, region="Assam"))

    def test_date_window_inclusive(self):
        d = date(2024, 7, 5)
        self.assertTrue(matches_filters(META, date_from=d, date_to=d))
        self.assertFalse(matches_filters(META, date_from=date(2024, 7, 6)))
        self.assertFalse(matches_filters(META, date_to=date(2024, 7, 4)))

    def test_missing_or_bad_date_excluded_when_filtering(self):
        self.assertFalse(matches_filters({}, date_from=date(2024, 1, 1)))
        self.assertFalse(matches_filters({"published": "July"}, date_to=date(2024, 12, 31)))

    def test_doc_types(self):
        self.assertTrue(matches_filters(META, doc_types=["bulletin", "report"]))
        self.assertFalse(matches_filters(META, doc_types=["report"]))

    def test_inverted_window_rejected(self):
        with self.assertRaises(ValueError):
            matches_filters(META, date_from=date(2024, 8, 1), date_to=date(2024, 7, 1))


if __name__ == "__main__":
    unittest.main()
