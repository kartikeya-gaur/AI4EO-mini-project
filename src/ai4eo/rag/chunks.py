"""Turn a document into chunks with stable IDs and metadata.

The splitting itself is injected (split_fn), so any splitter can be used and this
module stays testable without LangChain. Chunk size and overlap are not defaulted:
choose them with the retrieval evals (recall@k, MRR) and record them in
docs/decisions.md.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Sequence
from datetime import date

from ai4eo.schemas import Chunk

SplitFn = Callable[[str], Sequence[str]]


def chunk_id(source: str, index: int, text: str) -> str:
    """Deterministic ID. Changing the text or position changes the ID, which lets a
    re-index detect which chunks actually changed."""
    digest = hashlib.sha256(f"{source}\x1f{index}\x1f{text}".encode()).hexdigest()[:12]
    return f"c_{digest}"


def build_chunks(
    text: str,
    *,
    source: str,
    split_fn: SplitFn,
    doc_type: str = "",
    region: str = "",
    event: str = "",
    published: str = "",
) -> list[Chunk]:
    """Split text and attach metadata. `published` must be an ISO date (YYYY-MM-DD)."""
    if not source:
        raise ValueError("source is required so every chunk can be traced")
    if published:
        date.fromisoformat(published)  # raises ValueError if malformed

    base = {
        "source": source,
        "doc_type": doc_type,
        "region": region,
        "event": event,
        "published": published,
    }
    base = {k: v for k, v in base.items() if v}

    chunks: list[Chunk] = []
    for i, part in enumerate(split_fn(text)):
        part = part.strip()
        if not part:
            continue
        chunks.append(
            Chunk(
                id=chunk_id(source, i, part),
                text=part,
                source=source,
                metadata={**base, "chunk_index": str(i)},
            )
        )
    return chunks
