import unittest

from ai4eo.schemas import Chunk, Claim, ToolResult
from ai4eo.verify import verify_claims

TOOLS = [ToolResult("t1", "mask_area", {"flooded_km2": 412.0})]
CHUNKS = [Chunk("c1", "River crossed the danger level.", "CWC bulletin")]


def check(claims):
    return verify_claims(claims, TOOLS, CHUNKS, rel_tol=0.01)


def codes(claims):
    return [v.code for v in check(claims)]


class VerifyTests(unittest.TestCase):
    def test_valid_claims_pass(self):
        claims = [
            Claim("About 412 km2 flooded", "computed", "t1", "flooded_km2", 412.0),
            Claim("River crossed danger level", "contextual", "c1"),
        ]
        self.assertEqual(check(claims), [])

    def test_number_within_tolerance_passes(self):
        self.assertEqual(codes([Claim("x", "computed", "t1", "flooded_km2", 413.0)]), [])

    def test_number_mismatch(self):
        self.assertEqual(
            codes([Claim("x", "computed", "t1", "flooded_km2", 500.0)]), ["NUMBER_MISMATCH"]
        )

    def test_missing_source(self):
        self.assertEqual(codes([Claim("x", "contextual", None)]), ["MISSING_SOURCE"])

    def test_unknown_source(self):
        self.assertEqual(codes([Claim("x", "contextual", "c9")]), ["UNKNOWN_SOURCE"])
        self.assertEqual(codes([Claim("x", "computed", "t9")]), ["UNKNOWN_SOURCE"])

    def test_wrong_source_type(self):
        self.assertEqual(codes([Claim("x", "computed", "c1")]), ["WRONG_SOURCE_TYPE"])
        self.assertEqual(codes([Claim("x", "contextual", "t1")]), ["WRONG_SOURCE_TYPE"])

    def test_missing_field(self):
        self.assertEqual(codes([Claim("x", "computed", "t1", None, 412.0)]), ["MISSING_FIELD"])
        self.assertEqual(codes([Claim("x", "computed", "t1", "nope", 412.0)]), ["MISSING_FIELD"])

    def test_violation_reports_claim_index(self):
        claims = [
            Claim("ok", "contextual", "c1"),
            Claim("bad", "contextual", "c9"),
        ]
        self.assertEqual(check(claims)[0].claim_index, 1)


if __name__ == "__main__":
    unittest.main()
