"""Deterministic part of the Critic: structural checks on a draft's claims.

Checks that every claim cites an existing source of the right type and that every
structured number matches the tool output it cites. Whether a cited passage
actually supports a contextual sentence is a separate, LLM-based faithfulness
check (RAGAS) and is not done here.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from ai4eo.schemas import Chunk, Claim, ToolResult


@dataclass(frozen=True)
class Violation:
    code: str
    claim_index: int
    message: str


def verify_claims(
    claims: Sequence[Claim],
    tool_results: Sequence[ToolResult],
    chunks: Sequence[Chunk],
    *,
    rel_tol: float,
    abs_tol: float = 0.0,
) -> list[Violation]:
    tools = {t.id: t for t in tool_results}
    chunk_ids = {c.id for c in chunks}
    out: list[Violation] = []

    for i, c in enumerate(claims):
        if not c.source_id:
            out.append(Violation("MISSING_SOURCE", i, "claim cites nothing"))
            continue

        if c.kind == "computed":
            if c.source_id not in tools:
                code = "WRONG_SOURCE_TYPE" if c.source_id in chunk_ids else "UNKNOWN_SOURCE"
                out.append(Violation(code, i, f"computed claim cites {c.source_id!r}"))
                continue
            if c.value is None:
                continue
            values = tools[c.source_id].values
            if c.field_name is None or c.field_name not in values:
                out.append(Violation("MISSING_FIELD", i, f"no field {c.field_name!r} in result"))
            elif not math.isclose(c.value, values[c.field_name], rel_tol=rel_tol, abs_tol=abs_tol):
                out.append(
                    Violation(
                        "NUMBER_MISMATCH",
                        i,
                        f"claim says {c.value}, tool result says {values[c.field_name]}",
                    )
                )
        else:
            if c.source_id not in chunk_ids:
                code = "WRONG_SOURCE_TYPE" if c.source_id in tools else "UNKNOWN_SOURCE"
                out.append(Violation(code, i, f"contextual claim cites {c.source_id!r}"))

    return out
