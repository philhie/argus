"""M15: Impressum & Ownership Analysis — extract company info and emails.

Parses the Impressum/Imprint page of a German company website to extract
company details, executive names, email addresses, phone numbers, and
registration info. Enriches context for downstream modules (especially HIBP).

Usage: python -m argus.modules.ownership example-gmbh.de
"""

from __future__ import annotations

import logging
import re
from typing import Optional
from urllib.parse import urljoin

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.ownership")

# Regex patterns for German company forms
_COMPANY_RE = re.compile(
    r'([\w\s\-&.]+(?:GmbH|AG|KG|e\.K\.|UG|GmbH\s*&\s*Co\.\s*KG'
    r'|OHG|GbR|SE|eG|KGaA)(?:\s*\(haftungsbeschränkt\))?)',
    re.IGNORECASE,
)

# Geschäftsführer / Managing Director
_GF_RE = re.compile(
    r'(?:Geschäftsführer(?:in)?|Managing\s+Director|Vorstand|'
    r'Inhaber(?:in)?|Vertretungsberechtigte[r]?)'
    r'\s*[:\-]?\s*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,3})',
    re.UNICODE,
)

# Email — standard pattern
_EMAIL_RE = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
)

# Email — obfuscated [at] / (at) patterns
_EMAIL_OBFUSCATED_RE = re.compile(
    r'([a-zA-Z0-9._%+\-]+)\s*[\[\(]\s*(?:at|AT)\s*[\]\)]\s*'
    r'([a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
)

# Phone — German formats
_PHONE_RE = re.compile(
    r'(?:Tel(?:efon)?|Phone|Fon|Fax)'
    r'\s*[.:\-]?\s*'
    r'(\+?[\d\s/\-()]{7,20})',
    re.IGNORECASE,
)

# Handelsregister — HRB/HRA numbers
_REGISTER_RE = re.compile(
    r'(HR[AB]\s*\d{3,6}\s*[A-Z]?)',
    re.IGNORECASE,
)

# USt-IdNr — German VAT ID
_VAT_RE = re.compile(
    r'(DE\s?\d{9})',
)

# mailto: href extraction
_MAILTO_RE = re.compile(
    r'mailto:([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
    re.IGNORECASE,
)

_IMPRESSUM_PATHS = ["/impressum", "/imprint"]
_TIMEOUT = 10


def _fetch_impressum(domain: str) -> Optional[str]:
    """Fetch Impressum/Imprint page HTML. Returns None on failure."""
    try:
        import requests
    except ImportError:
        logger.debug("requests not installed, skipping impressum fetch")
        return None

    for path in _IMPRESSUM_PATHS:
        url = f"https://{domain}{path}"
        try:
            resp = requests.get(
                url,
                timeout=_TIMEOUT,
                allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ARGUS-Scanner/1.0)"},
            )
            if resp.status_code == 200 and len(resp.text) > 200:
                logger.debug("Fetched impressum from %s (%d bytes)", url, len(resp.text))
                return resp.text
        except Exception as exc:
            logger.debug("Failed to fetch %s: %s", url, exc)

    return None


def _extract_text(html: str) -> str:
    """Extract visible text from HTML using BeautifulSoup."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.debug("BeautifulSoup not installed, falling back to regex-only extraction")
        # Crude fallback: strip tags
        return re.sub(r'<[^>]+>', ' ', html)

    soup = BeautifulSoup(html, "html.parser")

    # Remove script/style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)


def _extract_mailto_emails(html: str) -> list[str]:
    """Extract emails from mailto: links in raw HTML."""
    return _MAILTO_RE.findall(html)


def _normalise_email(local: str, host: str) -> str:
    """Reconstruct email from obfuscated parts."""
    return f"{local.strip()}@{host.strip()}"


def _construct_gf_email(gf_name: str, domain: str) -> Optional[str]:
    """Try to construct an email from a GF name and domain.

    Attempts common German business email patterns:
      vorname.nachname@domain
      v.nachname@domain
    """
    parts = gf_name.strip().split()
    if len(parts) < 2:
        return None

    first = parts[0].lower()
    last = parts[-1].lower()

    # Normalise umlauts for email
    umlaut_map = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
    }
    for src, dst in umlaut_map.items():
        first = first.replace(src, dst)
        last = last.replace(src, dst)

    return f"{first}.{last}@{domain}"


def scan_ownership(domain: str) -> dict:
    """Scan impressum and return extracted ownership info dict."""
    info: dict = {
        "company_name": None,
        "executives": [],
        "emails": [],
        "phones": [],
        "register_number": None,
        "vat_id": None,
        "raw_text": None,
    }

    html = _fetch_impressum(domain)
    if not html:
        logger.debug("No impressum page found for %s", domain)
        return info

    text = _extract_text(html)
    info["raw_text"] = text[:5000]  # Cap stored text

    # Company name
    match = _COMPANY_RE.search(text)
    if match:
        info["company_name"] = match.group(1).strip()

    # Executives (Geschäftsführer)
    for m in _GF_RE.finditer(text):
        name = m.group(1).strip()
        if name not in info["executives"]:
            info["executives"].append(name)

    # Emails — from mailto: links in raw HTML
    mailto_emails = _extract_mailto_emails(html)

    # Emails — from visible text
    text_emails = _EMAIL_RE.findall(text)

    # Emails — obfuscated patterns
    obfuscated = _EMAIL_OBFUSCATED_RE.findall(text)
    obfuscated_emails = [_normalise_email(local, host) for local, host in obfuscated]

    # Deduplicate, preserving order
    seen: set[str] = set()
    all_emails: list[str] = []
    for email in mailto_emails + text_emails + obfuscated_emails:
        email_lower = email.lower().strip()
        if email_lower not in seen:
            seen.add(email_lower)
            all_emails.append(email_lower)

    info["emails"] = all_emails

    # Phone numbers
    for m in _PHONE_RE.finditer(text):
        phone = m.group(1).strip()
        if phone not in info["phones"]:
            info["phones"].append(phone)

    # Handelsregister
    match = _REGISTER_RE.search(text)
    if match:
        info["register_number"] = match.group(1).strip()

    # USt-IdNr
    match = _VAT_RE.search(text)
    if match:
        info["vat_id"] = match.group(1).replace(" ", "")

    return info


@register
class OwnershipModule(BaseModule):
    name = "ownership"
    description = "Impressum & Ownership Analysis"
    phase = 2
    step = 5

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        try:
            info = scan_ownership(domain)
        except Exception as exc:
            logger.debug("Ownership scan failed for %s: %s", domain, exc)
            return []

        # Store in context
        context.ownership_info = info

        # Update company name if we found one and context is empty
        if info["company_name"] and not context.company_name:
            context.company_name = info["company_name"]

        # Add discovered emails to context
        for email in info["emails"]:
            if email not in context.employee_emails:
                context.employee_emails.append(email)

        # Try to construct GF email if not already set
        if not context.gf_email and info["executives"]:
            constructed = _construct_gf_email(info["executives"][0], domain)
            if constructed:
                context.gf_email = constructed
                if constructed not in context.employee_emails:
                    context.employee_emails.append(constructed)

        # If we found a GF name and context doesn't have one, set it
        if not context.gf_name and info["executives"]:
            context.gf_name = info["executives"][0]

        # Context-enrichment only — no findings
        return []


# Standalone execution
if __name__ == "__main__":
    import json
    import sys

    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.ownership <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    print(f"Scanning impressum for {domain}...")
    info = scan_ownership(domain)

    print(f"\n{'='*60}")
    print(f"Ownership Info for {domain}")
    print(f"{'='*60}")

    # Print without raw_text for readability
    display = {k: v for k, v in info.items() if k != "raw_text"}
    print(json.dumps(display, indent=2, ensure_ascii=False))

    if info["raw_text"]:
        print(f"\nRaw text length: {len(info['raw_text'])} chars")
    else:
        print("\nNo impressum page found.")
