"""Plain data types shared by the deterministic tools and the Critic.

Standard library only, so these modules run and test without any ML dependencies.
The LangGraph state (Pydantic) is added in Week 3 and wraps these types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class Verdict(str, Enum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    NO_EVIDENCE = "no_evidence"


class Flag(str, Enum):
    RELIABLE = "reliable"
    UNRELIABLE = "unreliable"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class ConsistencyResult:
    verdict: Verdict
    reason: str
    residual_m: float | None = None
    tolerance_m: float | None = None
    n_points: int = 0


@dataclass(frozen=True)
class ReliabilityResult:
    flag: Flag
    reason: str


@dataclass(frozen=True)
class ToolResult:
    """Output of one deterministic tool call. Computed claims cite its id."""

    id: str
    tool: str
    values: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Chunk:
    """A retrieved document chunk. Contextual claims cite its id."""

    id: str
    text: str
    source: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


ClaimKind = Literal["computed", "contextual"]


@dataclass(frozen=True)
class Claim:
    """One claim in a draft report.

    Numbers must be emitted as structured fields (field_name, value) so they can
    be checked. Numbers written only inside free text are not checked here.
    """

    text: str
    kind: ClaimKind
    source_id: str | None
    field_name: str | None = None
    value: float | None = None
