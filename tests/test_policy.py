import unittest

from ai4eo.policy import reliability_flag
from ai4eo.schemas import ConsistencyResult, Flag, Verdict

OK = ConsistencyResult(Verdict.CONSISTENT, "ok")
BAD = ConsistencyResult(Verdict.INCONSISTENT, "mismatch")
NONE = ConsistencyResult(Verdict.NO_EVIDENCE, "no pass")
T = 0.5


def flag(c, s):
    return reliability_flag(c, s, shift_threshold=T).flag


class PolicyTests(unittest.TestCase):
    def test_inconsistent_always_unreliable(self):
        for s in (0.1, 0.9, None):
            self.assertIs(flag(BAD, s), Flag.UNRELIABLE)

    def test_consistent_low_shift_reliable(self):
        self.assertIs(flag(OK, 0.1), Flag.RELIABLE)

    def test_consistent_high_or_unknown_shift_unverified(self):
        self.assertIs(flag(OK, 0.9), Flag.UNVERIFIED)
        self.assertIs(flag(OK, None), Flag.UNVERIFIED)

    def test_no_evidence_never_reliable(self):
        self.assertIs(flag(NONE, 0.1), Flag.UNVERIFIED)
        self.assertIs(flag(NONE, None), Flag.UNVERIFIED)

    def test_no_evidence_high_shift_unreliable(self):
        self.assertIs(flag(NONE, 0.9), Flag.UNRELIABLE)

    def test_threshold_is_exclusive(self):
        self.assertIs(flag(OK, T), Flag.RELIABLE)

    def test_reason_is_present(self):
        self.assertTrue(reliability_flag(BAD, 0.1, shift_threshold=T).reason)


if __name__ == "__main__":
    unittest.main()
