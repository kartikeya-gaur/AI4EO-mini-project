import unittest

from ai4eo.rag.metrics import (
    mean_recall_at_k,
    mean_reciprocal_rank,
    recall_at_k,
    reciprocal_rank,
)


class MetricTests(unittest.TestCase):
    def test_recall_at_k(self):
        self.assertEqual(recall_at_k(["a", "b", "c"], {"b", "z"}, 2), 0.5)
        self.assertEqual(recall_at_k(["a", "b", "c"], {"b", "z"}, 1), 0.0)
        self.assertEqual(recall_at_k(["a", "b"], {"a"}, 5), 1.0)

    def test_duplicates_in_retrieved_do_not_inflate(self):
        self.assertEqual(recall_at_k(["a", "a", "a"], {"a", "b"}, 3), 0.5)

    def test_reciprocal_rank(self):
        self.assertEqual(reciprocal_rank(["x", "y", "a"], {"a"}), 1 / 3)
        self.assertEqual(reciprocal_rank(["a"], {"a"}), 1.0)
        self.assertEqual(reciprocal_rank(["x"], {"a"}), 0.0)

    def test_means(self):
        cases = [(["a", "b"], {"a"}), (["x", "a"], {"a"})]
        self.assertEqual(mean_reciprocal_rank(cases), 0.75)
        self.assertEqual(mean_recall_at_k(cases, 1), 0.5)
        self.assertEqual(mean_recall_at_k(cases, 2), 1.0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            recall_at_k(["a"], set(), 1)
        with self.assertRaises(ValueError):
            recall_at_k(["a"], {"a"}, 0)
        with self.assertRaises(ValueError):
            reciprocal_rank(["a"], [])
        with self.assertRaises(ValueError):
            mean_reciprocal_rank([])


if __name__ == "__main__":
    unittest.main()
