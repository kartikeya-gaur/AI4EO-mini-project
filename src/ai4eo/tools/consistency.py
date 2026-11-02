"""Altimetry consistency check (the project's differentiator).

Idea: within a reach the water surface is roughly level at a given moment, so the
terrain elevation along the edge of a correct flood mask should be close to the
altimetry water-surface height measured nearby around the same date.

No default uncertainty values are provided on purpose. Set them from the DEM and
altimetry product specifications and record the source in docs/decisions.md.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable

from ai4eo.schemas import ConsistencyResult, Verdict


def altimetry_consistency(
    boundary_elev_m: Iterable[float | None],
    altimetry_height_m: float | None,
    *,
    datum_offset_m: float,
    dem_sigma_m: float,
    altimetry_sigma_m: float,
    days_gap: float | None,
    max_gap_days: float,
    stage_rate_m_per_day: float,
    k: float = 2.0,
    min_points: int = 10,
) -> ConsistencyResult:
    """Compare DEM elevations along the mask boundary with an altimetry height.

    datum_offset_m is added to the DEM heights to express them in the altimetry
    datum (for example a geoid-to-ellipsoid offset). Compute it explicitly.

    The tolerance is k * sqrt(dem_sigma^2 + altimetry_sigma^2 + (rate * gap)^2),
    where the last term allows for the river stage changing between the flood
    image and the altimetry pass.
    """
    if min(dem_sigma_m, altimetry_sigma_m, stage_rate_m_per_day) < 0:
        raise ValueError("uncertainties and stage rate must be non-negative")
    if k <= 0 or min_points < 1 or max_gap_days < 0:
        raise ValueError("k and min_points must be positive, max_gap_days non-negative")

    if altimetry_height_m is None or days_gap is None:
        return ConsistencyResult(Verdict.NO_EVIDENCE, "no altimetry pass available")

    gap = abs(days_gap)
    if gap > max_gap_days:
        return ConsistencyResult(
            Verdict.NO_EVIDENCE,
            f"altimetry pass {gap:g} days from the image (limit {max_gap_days:g})",
        )

    values = [
        float(x) + datum_offset_m for x in boundary_elev_m if x is not None and math.isfinite(x)
    ]
    if len(values) < min_points:
        return ConsistencyResult(
            Verdict.NO_EVIDENCE,
            f"only {len(values)} valid boundary samples (need {min_points})",
            n_points=len(values),
        )

    residual = statistics.median(values) - altimetry_height_m
    tolerance = k * math.sqrt(
        dem_sigma_m**2 + altimetry_sigma_m**2 + (stage_rate_m_per_day * gap) ** 2
    )
    verdict = Verdict.CONSISTENT if abs(residual) <= tolerance else Verdict.INCONSISTENT
    reason = f"median boundary elevation differs from altimetry by {residual:+.2f} m "
    reason += f"(tolerance {tolerance:.2f} m)"
    return ConsistencyResult(verdict, reason, residual, tolerance, len(values))
