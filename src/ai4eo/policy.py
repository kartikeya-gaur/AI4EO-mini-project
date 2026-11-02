"""Baseline reliability policy. This is the rule the agent starts from.

The Validation agent may argue for a different flag, but must state a reason.
Ablation (README): flag quality with vs. without the altimetry check.
"""

from __future__ import annotations

from ai4eo.schemas import ConsistencyResult, Flag, ReliabilityResult, Verdict


def reliability_flag(
    consistency: ConsistencyResult,
    shift_score: float | None,
    *,
    shift_threshold: float,
) -> ReliabilityResult:
    """Combine the altimetry check and the shift score into a flag.

    consistency  shift      flag
    inconsistent any        unreliable
    consistent   low        reliable
    consistent   high/None  unverified
    no_evidence  high       unreliable
    no_evidence  low/None   unverified   (never "reliable" without a physical check)
    """
    if consistency.verdict is Verdict.INCONSISTENT:
        return ReliabilityResult(Flag.UNRELIABLE, f"altimetry check failed: {consistency.reason}")

    shift_known = shift_score is not None
    shift_high = shift_known and shift_score > shift_threshold

    if consistency.verdict is Verdict.CONSISTENT:
        if shift_known and not shift_high:
            return ReliabilityResult(
                Flag.RELIABLE, "altimetry consistent and scene near training data"
            )
        why = "shift score unknown" if not shift_known else "scene unlike training data"
        return ReliabilityResult(Flag.UNVERIFIED, f"altimetry consistent but {why}")

    if shift_high:
        return ReliabilityResult(
            Flag.UNRELIABLE, f"no altimetry evidence ({consistency.reason}) and high shift score"
        )
    return ReliabilityResult(Flag.UNVERIFIED, f"no altimetry evidence: {consistency.reason}")
