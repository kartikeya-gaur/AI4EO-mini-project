"""Retrieval metrics, computed on chunk IDs.

Each evaluation case is (retrieved_ids_in_rank_order, relevant_ids). Use these to
compare dense vs. hybrid vs. hybrid + rerank before looking at generation quality.
"""

from __future__ import annotations

from collections.abc import Collection, Sequence

Case = tuple[Sequence[str], Collection[str]]


def recall_at_k(retrieved: Sequence[str], relevant: Collection[str], k: int) -> float:
    if k < 1:
        raise ValueError("k must be at least 1")
    rel = set(relevant)
    if not rel:
        raise ValueError("a case needs at least one relevant id")
    return len(set(retrieved[:k]) & rel) / len(rel)


def reciprocal_rank(retrieved: Sequence[str], relevant: Collection[str]) -> float:
    rel = set(relevant)
    if not rel:
        raise ValueError("a case needs at least one relevant id")
    for rank, cid in enumerate(retrieved, start=1):
        if cid in rel:
            return 1.0 / rank
    return 0.0


def mean_recall_at_k(cases: Sequence[Case], k: int) -> float:
    if not cases:
        raise ValueError("no cases")
    return sum(recall_at_k(r, rel, k) for r, rel in cases) / len(cases)


def mean_reciprocal_rank(cases: Sequence[Case]) -> float:
    if not cases:
        raise ValueError("no cases")
    return sum(reciprocal_rank(r, rel) for r, rel in cases) / len(cases)
