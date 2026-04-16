"""Stage 2 — GF-impact score per finding.

Higher score = finding a German Geschäftsführer will actually react to.
Severity is the anchor; category weight, verifiability, and specific
high-signal finding IDs add bonuses on top.

Calibrated against the scoring matrix in the spec §8.5 — every row there
must match exactly, otherwise tier routing breaks.
"""

from __future__ import annotations

SEVERITY_WEIGHTS: dict[str, int] = {
    "KRITISCH": 10,
    "HOCH": 7,
    "MITTEL": 3,
    "NIEDRIG": 1,
    "INFO": 0,
}

CATEGORY_BONUS: dict[str, int] = {
    "exchange_exposure": 8,
    "credential_exposure": 6,
    "infrastructure": 4,
    "email_security": 3,
    "web_application": 2,
    "supply_chain": 1,
}

HIGH_VERIFIABILITY_MODULES: set[str] = {
    "shodan_lookup",
    "exchange",
    "file_exposure",
    "admin_panel",
    "source_maps",
    "google_dorking",
}

_CRITICAL_BOOST = 4
_VERIFIABILITY_BOOST = 5
_HIBP_PASSWORD_BOOST = 4
_EXPOSED_FILE_BOOST = 4
_EXCHANGE_ECP_BOOST = 5

_EXPOSED_FILE_IDS = {"FILE-WEBCONFIG", "FILE-ENV", "FILE-HTPASSWD", "FILE-GIT-CONFIG"}


def score_finding(finding: dict) -> int:
    """Return the GF-impact score for a single finding."""
    severity = finding.get("severity", "INFO")
    category = finding.get("category", "") or ""
    module = finding.get("module", "") or ""
    fid = finding.get("id", "") or ""

    score = SEVERITY_WEIGHTS.get(severity, 0)
    score += CATEGORY_BONUS.get(category, 0)

    if severity == "KRITISCH":
        score += _CRITICAL_BOOST

    if module in HIGH_VERIFIABILITY_MODULES:
        score += _VERIFIABILITY_BOOST

    if fid.startswith("CRED-001") or fid.startswith("CRED-004"):
        # CRED-004 (GF email in breach) is every bit as high-signal as
        # CRED-001 for cold outreach — it's the single most convertible
        # finding because it names the recipient personally.
        score += _HIBP_PASSWORD_BOOST

    if fid in _EXPOSED_FILE_IDS:
        score += _EXPOSED_FILE_BOOST

    if fid in {"EX-003", "EX-004"}:
        score += _EXCHANGE_ECP_BOOST

    return score


def score_findings(findings: list[dict]) -> list[dict]:
    """Attach score to each finding and return sorted descending."""
    scored = [{"finding": f, "score": score_finding(f)} for f in findings]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored
