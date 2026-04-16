"""Pre-processing that runs before filter/score: aggregate noisy repeats.

The scanner emits one finding per discovered CVE and one finding per
admin/database/staging subdomain. For a prospect email we want one
compact finding per theme, not ten rows of the same story. Without this
step, Microstep's top 3 would be {phpMyAdmin, Adminer, MySQL} on three
different URLs — the prospect reads "database" three times.
"""

from __future__ import annotations

import re

_IP_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")

_SUB_TITLES = {
    "SUB-001": "{count} Staging-Subdomains öffentlich erreichbar",
    "SUB-002": "{count} Admin-Panel-Subdomains öffentlich erreichbar",
    "SUB-004": "{count} Datenbank-Subdomains öffentlich erreichbar",
}


def aggregate_cve_findings(findings: list[dict]) -> list[dict]:
    """Collapse multiple SHO-002 CVE findings on the same IP into one.

    The scanner emits one SHO-002 per CVE, so one IP can produce 10+ rows
    of the same story. We rewrite them into a single 'N ungepatchte CVEs
    auf {ip}' finding per IP, preserving all CVE IDs for the template.
    """
    cve = [f for f in findings if f.get("id") == "SHO-002"]
    rest = [f for f in findings if f.get("id") != "SHO-002"]

    if len(cve) <= 1:
        return findings

    by_ip: dict[str, list[dict]] = {}
    for f in cve:
        ip_match = _IP_RE.search(f.get("evidence", "") or "")
        ip = ip_match.group(0) if ip_match else "unknown"
        by_ip.setdefault(ip, []).append(f)

    for ip, group in by_ip.items():
        if len(group) == 1:
            rest.append(group[0])
            continue
        all_cves: list[str] = []
        for f in group:
            all_cves.extend(f.get("cve_ids", []) or [])
        aggregated = dict(group[0])
        aggregated["title"] = f"{len(all_cves)} ungepatchte CVEs auf {ip}"
        aggregated["cve_ids"] = all_cves
        aggregated["id"] = "SHO-002-AGG"
        rest.append(aggregated)

    return rest


def dedup_subdomain_findings(findings: list[dict]) -> list[dict]:
    """Collapse multiple SUB-001/SUB-002/SUB-004 into one per type."""
    groups: dict[str, list[dict]] = {}
    others: list[dict] = []
    for f in findings:
        fid = f.get("id", "") or ""
        if fid in _SUB_TITLES:
            groups.setdefault(fid, []).append(f)
        else:
            others.append(f)

    for fid, group in groups.items():
        if len(group) == 1:
            others.append(group[0])
            continue
        rep = dict(group[0])
        rep["title"] = _SUB_TITLES[fid].format(count=len(group))
        others.append(rep)

    return others


def preprocess(findings: list[dict]) -> list[dict]:
    """Apply all pre-processing passes in order."""
    out = aggregate_cve_findings(findings)
    out = dedup_subdomain_findings(out)
    return out
