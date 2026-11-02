import unittest

from ai4eo.schemas import Verdict
from ai4eo.tools.consistency import altimetry_consistency

BASE = dict(
    datum_offset_m=0.0,
    dem_sigma_m=1.0,
    altimetry_sigma_m=0.1,
    days_gap=0.0,
    max_gap_days=10.0,
    stage_rate_m_per_day=0.5,
)


def run(elev, alt, **over):
    args = {**BASE, **over}
    return altimetry_consistency(elev, alt, **args)


class ConsistencyTests(unittest.TestCase):
    def test_consistent(self):
        r = run([38.0] * 20, 38.2)
        self.assertIs(r.verdict, Verdict.CONSISTENT)
        self.assertAlmostEqual(r.residual_m, -0.2)
        self.assertAlmostEqual(r.tolerance_m, 2 * (1.0 + 0.01) ** 0.5)

    def test_inconsistent(self):
        r = run([45.0] * 20, 38.0)
        self.assertIs(r.verdict, Verdict.INCONSISTENT)

    def test_no_pass(self):
        r = run([38.0] * 20, None)
        self.assertIs(r.verdict, Verdict.NO_EVIDENCE)

    def test_missing_gap_is_no_evidence(self):
        r = run([38.0] * 20, 38.0, days_gap=None)
        self.assertIs(r.verdict, Verdict.NO_EVIDENCE)

    def test_gap_too_large(self):
        r = run([38.0] * 20, 38.0, days_gap=11.0)
        self.assertIs(r.verdict, Verdict.NO_EVIDENCE)

    def test_negative_gap_uses_absolute_value(self):
        r = run([38.0] * 20, 38.0, days_gap=-11.0)
        self.assertIs(r.verdict, Verdict.NO_EVIDENCE)

    def test_too_few_points(self):
        r = run([38.0] * 5, 38.0)
        self.assertIs(r.verdict, Verdict.NO_EVIDENCE)
        self.assertEqual(r.n_points, 5)

    def test_nan_and_none_ignored(self):
        elev = [38.0] * 10 + [float("nan"), None]
        r = run(elev, 38.0)
        self.assertIs(r.verdict, Verdict.CONSISTENT)
        self.assertEqual(r.n_points, 10)

    def test_datum_offset_applied(self):
        # DEM heights in a different datum: 20.0 + 18.2 = 38.2 in the altimetry datum.
        self.assertIs(run([20.0] * 20, 38.2, datum_offset_m=18.2).verdict, Verdict.CONSISTENT)
        self.assertIs(run([20.0] * 20, 38.2).verdict, Verdict.INCONSISTENT)

    def test_stage_change_widens_tolerance(self):
        elev = [41.0] * 20  # residual +3.0 m
        self.assertIs(run(elev, 38.0, days_gap=0.0).verdict, Verdict.INCONSISTENT)
        r = run(elev, 38.0, days_gap=5.0)
        self.assertIs(r.verdict, Verdict.CONSISTENT)
        self.assertAlmostEqual(r.tolerance_m, 2 * (1.0 + 0.01 + 6.25) ** 0.5)

    def test_median_resists_outliers(self):
        elev = [38.0] * 18 + [200.0, 300.0]
        self.assertIs(run(elev, 38.0).verdict, Verdict.CONSISTENT)

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            run([38.0] * 20, 38.0, dem_sigma_m=-1.0)
        with self.assertRaises(ValueError):
            run([38.0] * 20, 38.0, k=0.0)


if __name__ == "__main__":
    unittest.main()
