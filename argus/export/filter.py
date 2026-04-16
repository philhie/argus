"""Stage 1 — drop noise before scoring.

Handles three kinds of noise the scanner emits:
  1. INFO-severity findings (never GF-relevant)
  2. Cosmetic IDs (CAA, BIMI, header leaks, cloud-hosting-detected)
  3. GitHub false positives — repo owners who index millions of domains
     (ad-blocker lists, expired-domain dumps, generic data repos).

A GitHub finding is only kept when the repo path contains the company
name as a real component, AND the owner/path doesn't match a noise
pattern.
"""

from __future__ import annotations

import re

# Repo owners whose output is always noise — they index domain strings at scale.
GITHUB_NOISE_OWNERS = {
    # Expired domain name lists
    "cirosantilli",

    # Ad-blocker / privacy filter lists
    "MajkiIT", "alsyundawy", "kalyanch8", "vaisx05",
    "bunnyblueair", "kusumata", "antelope-app", "Emyori",
    "LoveMyself546", "clash1step", "zenkiet",

    # Generic data dumps / URL lists / crawl outputs
    "swrdfgd", "tech234a", "rubyroidlabs", "OstinUA",
    "pasxalisbekos", "Shu4bham", "ziguinchor", "DavidGil92",

    # Open source projects where "domain.com" appears in config examples
    "apache", "GNOME", "oracle", "Alluxio", "frida",
    "cockroachlabs", "valum-framework",

    # Vala/GNOME checksum.compute_for_string false positives
    "vala-lang", "blaztinn", "AmbitionFramework", "Simpleyyt",
    "amir1376", "tiliado", "milohr", "blankon-packages",
    "tliron", "google-code-export", "meehow", "Rirusha",

    # Crypto/blockchain where "checksum.com" matches
    "michealbrownm", "patricknoir", "moserware",

    # Hadoop/HDFS where "checksum.com" is a config key
    "JakubNei", "AvistoTelecom", "niegl", "slydlake",

    # Security research / phishing detection datasets
    "r3dxpl0it", "beerphilipp",

    # Ticket system / exam datasets (contain random domains)
    "wix-incubator", "Yairsep-zz", "suvelocity", "shlior7",
    "Idokah", "ocentra",

    # Outreach / enrichment tools (contain target lists)
    "JoshAugust", "BrijAtIISc", "eventjuicer",

    # Other specific false positive sources
    "LDSSA", "daxroc", "appbricks", "bnaylor",
    "maranemil", "rahultoppur", "sarge6", "keksgauner",
    "dreisman", "SystemJargon",

    # AI/ML training data repos
    "Tru-North", "Sawan-Kushwah", "fhnw-cs",

    # MapReduce / data processing output
    "jasbir90", "jaybro2017", "billpugh", "vitorueno",
}

GITHUB_NOISE_PATH_PATTERNS = [
    "expired-domain-names",
    "pihole", "pi-hole",
    "easyprivacy",
    "polish-ads-filter",
    "adsblocker", "AdBlock", "adguard",
    "blacklist", "blocklist",
    "rule-provider",
    "domain-database",
    "tld_lists",
    "annotation-urls",
    "WebsiteUrlScanner",
    "RandomWebsite",
    "MapReduce-WARC",
    "phishing", "PHISHING_URL",
    "PIIxel_Leaks", "Tranco1M",
    "found_nothing",
    "extras/rails.csv",
    "hexlet-2021",
    "SafeSurf",
    "dns-blocklists",
    "data/rank/shards",
    "ticket-manager",
    "entry-level-exam",
    "TicketSystem", "TicketingSystem",
]

# German legal-form suffixes — stripped before comparing company identifiers.
LEGAL_SUFFIXES = [
    " gmbh & co. kg", " gmbh & co kg", " gmbh", " ag", " se",
    " ug", " kg", " ohg", " e.k.", " inc", " inc.", " ltd",
    " ltd.", " llc", " corp", " corp.", " plc", " sa", " sas",
]


def normalize_company(name: str) -> str:
    """Lowercase, strip legal suffixes, remove non-alphanumerics."""
    if not name:
        return ""
    n = name.lower()
    for suffix in LEGAL_SUFFIXES:
        if n.endswith(suffix):
            n = n[: -len(suffix)]
            break
    return re.sub(r"[^a-z0-9]", "", n)


# Minimum length for a normalized name to be a usable ownership signal.
# Below this, path-component matching produces too many false positives
# (e.g. "ag" in "flag", "se" in "sentry").
_MIN_COMPANY_LEN = 4


def is_company_owned_github(finding: dict, company_norm: str) -> bool:
    """Return True if a GitHub finding plausibly belongs to the company.

    A finding passes only when:
      1. company_norm is long enough to be distinctive (>= 4 chars)
      2. Owner is not in the noise blocklist
      3. Path doesn't match any noise pattern
      4. Either the company name appears as a path component,
         or the normalized owner contains the company name.
    """
    if len(company_norm) < _MIN_COMPANY_LEN:
        return False

    evidence = finding.get("evidence", "") or ""

    owner_match = re.search(r"github\.com/([^/\s]+)/", evidence)
    if not owner_match:
        return False
    owner = owner_match.group(1)

    if owner in GITHUB_NOISE_OWNERS:
        return False

    evidence_lower = evidence.lower()
    for pattern in GITHUB_NOISE_PATH_PATTERNS:
        if pattern.lower() in evidence_lower:
            return False

    # Positive: company name is a full path component
    path_match = re.search(r"github\.com/([^\s?]+)", evidence)
    if path_match:
        url_path = path_match.group(1).lower()
        # Split on typical path + filename separators
        components = re.split(r"[/\-_.]", url_path)
        for comp in components:
            if comp == company_norm and len(comp) >= _MIN_COMPANY_LEN - 1:
                return True

    # Positive: owner name contains the company name
    owner_norm = normalize_company(owner)
    if owner_norm and company_norm in owner_norm:
        return True

    return False


# Prefixes / exact IDs that are cosmetic and always dropped before scoring.
_COSMETIC_PREFIXES = (
    "CAA-001",      # no CAA records — generic DNS hygiene
    "DNS-009",      # no BIMI — nice-to-have
    "HDR-LEAK",     # server header info leaks — dev concern
    "IP-001",       # cloud-hosting detected — not a finding
    "IP-003",       # no reverse DNS — too technical
)

_COSMETIC_EXACT = {
    "CLOUD-002",    # private bucket exists — not exposed
}


def _is_cosmetic(fid: str, title: str, module: str) -> bool:
    if fid in _COSMETIC_EXACT:
        return True
    if any(fid.startswith(p) for p in _COSMETIC_PREFIXES):
        return True
    # WB-002 is only cosmetic when the pattern is a sitemap entry
    if fid == "WB-002" and "sitemap" in title.lower():
        return True
    return False


def filter_findings(findings: list[dict], company_name: str) -> list[dict]:
    """Drop INFO, cosmetic, and GitHub-noise findings."""
    company_norm = normalize_company(company_name)
    kept: list[dict] = []
    for f in findings:
        severity = f.get("severity", "INFO")
        if severity == "INFO":
            continue

        fid = f.get("id", "") or ""
        module = f.get("module", "") or ""
        title = f.get("title", "") or ""

        if _is_cosmetic(fid, title, module):
            continue

        if module == "github_secrets":
            if not is_company_owned_github(f, company_norm):
                continue

        kept.append(f)
    return kept
