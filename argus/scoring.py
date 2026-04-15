"""M16: Exposure Score Calculation.

Weighted scoring across 6 categories. Higher = more exposed = worse.
"""

from __future__ import annotations

from argus.models import Finding, ScoreBreakdown, Severity

SCORE_WEIGHTS = {
    "email_security": 0.20,
    "infrastructure": 0.25,
    "web_application": 0.20,
    "credential_exposure": 0.15,
    "exchange_exposure": 0.10,
    "supply_chain": 0.10,
}

SEVERITY_POINTS = {
    Severity.CRITICAL: 25,
    Severity.HIGH: 15,
    Severity.MEDIUM: 8,
    Severity.LOW: 3,
    Severity.INFO: 0,
}


def calculate_exposure_score(findings: list[Finding]) -> tuple[int, ScoreBreakdown]:
    """Calculate 0-100 exposure score. Higher = more exposed = worse."""
    category_raw: dict[str, int] = {}

    for f in findings:
        cat = f.category
        points = SEVERITY_POINTS.get(f.severity, 0)
        category_raw[cat] = category_raw.get(cat, 0) + points

    # Normalize each category to 0-100
    breakdown = ScoreBreakdown()
    for cat in SCORE_WEIGHTS:
        raw = category_raw.get(cat, 0)
        normalized = min(100, raw)
        setattr(breakdown, cat, normalized)

    # Weighted total
    total = sum(
        getattr(breakdown, cat) * weight
        for cat, weight in SCORE_WEIGHTS.items()
    )

    return min(100, int(total)), breakdown
