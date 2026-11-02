"""Validate filters that an LLM extracted from a user question.

The Context agent may ask a model to turn "Assam floods in July 2024, official bulletins"
into {region, date_from, date_to, doc_types}. Model output is untrusted input: it is
checked against a closed schema and a closed set of allowed values before it touches the
retriever. Anything else raises FilterError, and the caller decides what to do (for
example retry, or search unfiltered and say so in the report).
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from datetime import date

from ai4eo.rag.filters import matches_filters

_ALLOWED_KEYS = {"region", "date_from", "date_to", "doc_types"}


class FilterError(ValueError):
    pass


@dataclass(frozen=True)
class Filters:
    region: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    doc_types: tuple[str, ...] | None = None

    def matches(self, metadata: Mapping[str, str]) -> bool:
        return matches_filters(
            metadata,
            region=self.region,
            date_from=self.date_from,
            date_to=self.date_to,
            doc_types=self.doc_types,
        )


def _parse_date(name: str, value: object) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise FilterError(f"{name} must be an ISO date string or null")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise FilterError(f"{name} is not a valid ISO date: {value!r}") from exc


def parse_filters(
    raw: Mapping[str, object],
    *,
    allowed_regions: Collection[str],
    allowed_doc_types: Collection[str],
) -> Filters:
    unknown = set(raw) - _ALLOWED_KEYS
    if unknown:
        raise FilterError(f"unknown filter keys: {sorted(unknown)}")

    region = raw.get("region")
    if region is not None:
        if not isinstance(region, str):
            raise FilterError("region must be a string or null")
        by_fold = {r.casefold(): r for r in allowed_regions}
        if region.casefold() not in by_fold:
            raise FilterError(f"region {region!r} is not in the allowed list")
        region = by_fold[region.casefold()]

    date_from = _parse_date("date_from", raw.get("date_from"))
    date_to = _parse_date("date_to", raw.get("date_to"))
    if date_from and date_to and date_from > date_to:
        raise FilterError("date_from is after date_to")

    doc_types = raw.get("doc_types")
    if doc_types is not None:
        if not isinstance(doc_types, (list, tuple)) or not all(
            isinstance(d, str) for d in doc_types
        ):
            raise FilterError("doc_types must be a list of strings or null")
        bad = [d for d in doc_types if d not in set(allowed_doc_types)]
        if bad:
            raise FilterError(f"doc_types not allowed: {bad}")
        doc_types = tuple(doc_types)

    return Filters(region, date_from, date_to, doc_types)
