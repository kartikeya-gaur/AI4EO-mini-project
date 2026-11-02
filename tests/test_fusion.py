import unittest

from ai4eo.rag.fusion import reciprocal_rank_fusion

K = 60


class FusionTests(unittest.TestCase):
    def test_scores_and_order(self):
        fused = reciprocal_rank_fusion([["a", "b", "c"], ["b", "c", "d"]], k=K)
        ids = [i for i, _ in fused]
        self.assertEqual(ids, ["b", "c", "a", "d"])
        scores = dict(fused)
        self.assertAlmostEqual(scores["b"], 1 / 62 + 1 / 61)
        self.assertAlmostEqual(scores["a"], 1 / 61)

    def test_item_in_both_lists_beats_single_top_hit(self):
        fused = reciprocal_rank_fusion([["x", "a"], ["y", "a"]], k=K)
        self.assertEqual(fused[0][0], "a")

    def test_repeat_within_list_counts_once(self):
        fused = dict(reciprocal_rank_fusion([["a", "a", "a"]], k=K))
        self.assertAlmostEqual(fused["a"], 1 / 61)

    def test_ties_keep_first_seen_order(self):
        fused = reciprocal_rank_fusion([["a"], ["b"]], k=K)
        self.assertEqual([i for i, _ in fused], ["a", "b"])

    def test_empty_inputs(self):
        self.assertEqual(reciprocal_rank_fusion([], k=K), [])
        self.assertEqual(reciprocal_rank_fusion([[], []], k=K), [])

    def test_negative_k_rejected(self):
        with self.assertRaises(ValueError):
            reciprocal_rank_fusion([["a"]], k=-1)


if __name__ == "__main__":
    unittest.main()
