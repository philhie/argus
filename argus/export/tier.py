"""Stage 3 — map scored findings to a campaign tier.

Tiers drive which Instantly sub-sequence a lead lands in:
    A — high-impact, verifiable finding → aggressive 5-touch sequence
    B — credible finding but needs multi-point framing
    C — mail-auth / soft-signal leads (conservative copy)
    SKIP — nothing worth emailing about

Thresholds match the main spec body (§9). If production shows that too
many leads land in A, raise the A threshold to 20 — the upgrade rule in
maybe_upgrade provides an escape hatch for multi-finding B leads that
deserve A copy.
"""

from __future__ import annotations

TIER_THRESHOLDS: dict[str, int] = {
    "A": 18,
    "B": 10,
    "C": 5,
}

_MULTI_FINDING_UPGRADE_COUNT = 3
_MULTI_FINDING_UPGRADE_FLOOR = 10


def classify_tier(scored_findings: list[dict]) -> str:
    """Return 'A' | 'B' | 'C' | 'SKIP' based on the top finding score."""
    if not scored_findings:
        return "SKIP"
    top_score = scored_findings[0]["score"]
    if top_score >= TIER_THRESHOLDS["A"]:
        return "A"
    if top_score >= TIER_THRESHOLDS["B"]:
        return "B"
    if top_score >= TIER_THRESHOLDS["C"]:
        return "C"
    return "SKIP"


def maybe_upgrade(tier: str, scored_findings: list[dict]) -> str:
    """Upgrade B → A when 3+ findings score >= 10.

    Rationale: individually moderate findings that compound into a clear
    attack path deserve Tier A copy — the prospect has enough to worry
    about even if no single finding is 'critical'.
    """
    if tier != "B":
        return tier
    high_count = sum(
        1 for f in scored_findings if f["score"] >= _MULTI_FINDING_UPGRADE_FLOOR
    )
    if high_count >= _MULTI_FINDING_UPGRADE_COUNT:
        return "A"
    return tier
