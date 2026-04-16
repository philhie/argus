"""Apollo lead CSV reading + per-lead enrichment helpers.

Apollo exports have unpredictable column names (case, spaces, hyphens,
underscores mixed). We normalize once at read time and look up values
by the canonical form.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterator

HOURLY_COST_EUR = 30
DOWNTIME_HOURS = 8

# Subdomain prefixes that make for more-concrete subject lines than the
# bare apex domain. Order matters — first match wins.
_INTERESTING_PREFIXES = (
    "mail.", "admin.", "exchange.", "owa.", "autodiscover.",
    "vpn.", "remote.", "webmail.", "db.", "mysql.", "staging.",
)


def _canon(name: str) -> str:
    """Canonical column-name form: lowercase, alphanumerics only."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


# Canonical-name → list of accepted aliases. First alias is the preferred key.
_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "email":          ("email", "emailaddress", "primaryemail"),
    "first_name":     ("firstname", "first"),
    "last_name":      ("lastname", "last", "surname"),
    "title":          ("title", "jobtitle", "position"),
    "company_domain": ("companydomain", "domain", "website"),
    "company_name":   ("companyname", "company", "account"),
    "linkedin_url":   ("linkedinurl", "linkedin"),
    "industry":       ("industry",),
    "company_size":   ("companysize", "size"),
    "city":           ("city",),
    "employee_count": ("employeecount", "employees", "numberofemployees"),
}


def _remap_row(row: dict) -> dict:
    """Return a new dict with canonical keys, empty string for missing."""
    canon_input = {_canon(k): (v or "").strip() for k, v in row.items() if k}
    out: dict = {}
    for canonical, aliases in _COLUMN_ALIASES.items():
        value = ""
        for alias in aliases:
            if alias in canon_input and canon_input[alias]:
                value = canon_input[alias]
                break
        out[canonical] = value
    return out


def read_leads(path: Path) -> Iterator[dict]:
    """Yield canonicalized lead dicts from an Apollo-style CSV."""
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            yield _remap_row(raw)


def calc_downtime(employee_count: str) -> str:
    """Rounded downtime cost for the body: 'rund 20.000€'.

    Returns empty string when employee_count isn't a usable number, so the
    email template can omit the sentence rather than render 'rund €'.
    """
    if not employee_count:
        return ""
    try:
        n = int(str(employee_count).strip().replace(",", "").replace(".", ""))
    except ValueError:
        return ""
    if n <= 0:
        return ""
    cost = n * HOURLY_COST_EUR * DOWNTIME_HOURS
    # Round to nearest 1000 for clean copy.
    rounded = int(round(cost / 1000.0)) * 1000
    # German thousands separator uses '.' not ','.
    return "rund {}€".format(f"{rounded:,}".replace(",", "."))


def pick_subdomain(scan_data: dict) -> str:
    """Pick a notable subdomain from scan evidence, else return the apex."""
    domain = scan_data.get("domain", "") or ""
    if not domain:
        return ""
    pattern = re.compile(rf"\b([a-z0-9-]+\.{re.escape(domain)})", re.IGNORECASE)
    for f in scan_data.get("findings", []) or []:
        ev = f.get("evidence", "") or ""
        m = pattern.search(ev)
        if not m:
            continue
        sub = m.group(1).lower()
        for prefix in _INTERESTING_PREFIXES:
            if sub.startswith(prefix):
                return sub
    return domain
