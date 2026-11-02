"""Reciprocal rank fusion (RRF).

Combines several ranked lists of chunk IDs into one. The same function serves two uses:
fusing the results of several rewritten queries (multi-query / RAG-fusion) and fusing
dense with sparse (BM25) results in hybrid retrieval.

score(id) = sum over lists of 1 / (k + rank), rank starting at 1.
k is required, with no default. The original RRF paper (Cormack et al., 2009) used 60;
confirm that and tune it on your own retrieval evals.
"""

from __future__ import annotations

from collections.abc import Sequence


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[str]], *, k: int
) -> list[tuple[str, float]]:
    if k < 0:
        raise ValueError("k must be non-negative")

    scores: dict[str, float] = {}
    first_seen: dict[str, int] = {}
    order = 0
    for ranking in rankings:
        seen_in_list: set[str] = set()
        for rank, cid in enumerate(ranking, start=1):
            if cid in seen_in_list:  # a repeat within one list counts once
                continue
            seen_in_list.add(cid)
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
            if cid not in first_seen:
                first_seen[cid] = order
                order += 1

    # Highest score first; ties keep the order in which an ID first appeared.
    return sorted(scores.items(), key=lambda item: (-item[1], first_seen[item[0]]))
