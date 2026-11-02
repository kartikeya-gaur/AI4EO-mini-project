"""Metadata filters applied before (or alongside) vector search.

A filter that is set but cannot be evaluated (missing or malformed metadata) excludes
the chunk. Excluding is the safe default for a system that must not cite the wrong
event or the wrong period.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
from datetime import date


def matches_filters(
    metadata: Mapping[str, str],
    *,
    region: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    doc_types: Collection[str] | None = None,
) -> bool:
    if date_from and date_to and date_from > date_to:
        raise ValueError("date_from must not be after date_to")

    if region is not None and metadata.get("region", "").casefold() != region.casefold():
        return False

    if doc_types is not None and metadata.get("doc_type") not in set(doc_types):
        return False

    if date_from is not None or date_to is not None:
        raw = metadata.get("published", "")
        try:
            published = date.fromisoformat(raw)
        except ValueError:
            return False
        if date_from is not None and published < date_from:
            return False
        if date_to is not None and published > date_to:
            return False

    return True
