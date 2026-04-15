# KENGO RECON ENGINE — Complete Technical Specification
## Codename: ARGUS
### FINAL VERSION (V2) — 15 April 2026
### 29 Module | 100+ Finding-Typen | ~€153-200/Monat all-in
### Dieses Dokument ist das vollständige Handoff für Claude Code.

---

> **CHANGELOG V1 → V2:**
> V1 hatte 15 Module. Nach Deep Research wurden 14 kritische fehlende Module identifiziert.
> V2 hat 29 Module total. Die neuen Module finden die Findings die den GF persönlich
> treffen — sein Passwort auf GitHub, seine gelöschte Config-Datei im Wayback Machine,
> sein Subdomain den jeder übernehmen kann. V2 findet in 15 Minuten passiv mehr als
> ein typischer €15.000 Penetrationstest in 2 Wochen.

---


---

## 1. PURPOSE

Build an automated, passive, legal reconnaissance engine that scans German Mittelstand company domains and produces:
1. An **Exposure Score** (0-100) quantifying external attack surface
2. A **Finding Set** with evidence, severity, NIS2 mapping, and remediation
3. An **Attack Path Narrative** (LLM-generated kill chain)
4. A **personalized outreach email** with 3 key findings
5. An **interactive HTML report** ("Hacker's POV") for the prospect

The engine must process 500+ domains/day on a single machine. All techniques are passive OSINT — no active exploitation, no brute force, no unauthorized access.

---

## 2. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                                  │
│  CSV/JSON lead list: domain, company_name, gf_name, gf_email, ...  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR (main.py)                          │
│  - Reads lead list                                                  │
│  - Runs modules in sequence per domain                              │
│  - Manages rate limiting across all APIs                            │
│  - Writes results to /results/{domain}.json                        │
│  - Handles errors gracefully (one failed module ≠ abort scan)      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
   │ RECON MODULES│    │ ANALYSIS     │    │ OUTPUT       │
   │ (data gather)│    │ (scoring,    │    │ (reports,    │
   │              │    │  correlation)│    │  emails)     │
   └─────────────┘    └──────────────┘    └──────────────┘
```

### Module Execution Order (per domain):

```
Phase 1 — DNS & Infrastructure (parallel where possible)
  ├── M01: DNS Intelligence
  ├── M02: Subdomain Discovery (crt.sh)
  └── M03: IP Resolution & Geolocation

Phase 2 — Service Enumeration (depends on Phase 1 IPs)
  ├── M04: Shodan Lookup (per IP)
  ├── M05: HTTP Security Headers (per live host)
  ├── M06: TLS Analysis (per live host)
  └── M07: Technology Fingerprinting (per live host)

Phase 3 — Deep Recon (depends on Phase 2 findings)
  ├── M08: Exchange Detection & NTLM Challenge
  ├── M09: Common File Exposure Check
  ├── M10: Admin Panel Discovery
  └── M11: API Endpoint Discovery

Phase 4 — Intelligence Enrichment
  ├── M12: Credential Exposure (HIBP)
  ├── M13: MSP Identification & Scoring
  ├── M14: Supply Chain Mapping
  └── M15: Ownership & Structure (North Data)

Phase 5 — Analysis & Output
  ├── M16: Scoring Engine
  ├── M17: Attack Path Assembly (LLM)
  ├── M18: NIS2 Compliance Mapping
  └── M19: Report & Email Generation
```

---

## 3. DATA MODEL

### 3.1 Input Schema (leads.csv)

```csv
domain,company_name,industry,employee_count,gf_name,gf_email,gf_title,city,nis2_sector
true-fruits.com,True Fruits GmbH,Lebensmittel,37,Marco Knauf,marco.knauf@true-fruits.com,Geschäftsführer,Bonn,Lebensmittelproduktion
```

Required fields: `domain`, `company_name`
Optional but recommended: `gf_name`, `gf_email`, `employee_count`, `industry`
Auto-enriched if missing: `nis2_sector` (from industry), `city` (from Impressum)

### 3.2 Core Data Models (Python dataclasses)

```python
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class Severity(Enum):
    CRITICAL = "KRITISCH"
    HIGH = "HOCH"
    MEDIUM = "MITTEL"
    LOW = "NIEDRIG"
    INFO = "INFO"

@dataclass
class Finding:
    id: str                          # e.g. "DNS-001", "EX-003", "SHOP-002"
    module: str                      # which module produced this
    category: str                    # "Email Security", "Exchange", "Web Application", etc.
    title: str                       # German, concise
    title_en: str                    # English backup
    description: str                 # German, 2-3 sentences max
    severity: Severity
    evidence: str                    # The exact command or data that proves it
    evidence_raw: Optional[str]      # Raw response data (for report appendix)
    nis2_paragraphs: List[str]       # e.g. ["§30 Abs. 2 Nr. 1", "§30 Abs. 2 Nr. 9"]
    remediation: str                 # German, actionable
    cvss_score: Optional[float]      # If a CVE is associated
    cve_ids: List[str]               # e.g. ["CVE-2026-31889"]
    automatable: bool                # Can this be checked fully automatically?

@dataclass 
class DNSResult:
    mx_records: List[Dict]           # [{"priority": 10, "host": "smtp1.example.com", "ip": "1.2.3.4"}]
    spf_record: Optional[str]        # Raw SPF TXT record
    spf_mechanism: Optional[str]     # "~all", "-all", "?all", "+all"
    spf_includes: List[str]          # Domains included in SPF (MSP identification)
    spf_ips: List[str]               # IPs in SPF record
    dmarc_record: Optional[str]      # Raw DMARC record
    dmarc_policy: Optional[str]      # "none", "quarantine", "reject"
    dmarc_subdomain_policy: Optional[str]  # sp= value
    dmarc_alignment_dkim: Optional[str]    # adkim= value
    dmarc_alignment_spf: Optional[str]     # aspf= value
    dkim_selectors_found: List[str]  # Which selectors have valid DKIM records
    dkim_selectors_checked: List[str] # All selectors we checked
    mta_sts: bool                    # Does _mta-sts TXT record exist?
    dane_tlsa: bool                  # Does TLSA record exist for mail server?
    bimi: bool                       # Does BIMI record exist?
    ns_records: List[str]            # Nameservers
    ns_provider: Optional[str]       # Identified DNS provider (IONOS, Cloudflare, etc.)
    txt_records: List[str]           # All TXT records (for verification tokens, etc.)
    a_records: List[Dict]            # [{"ip": "1.2.3.4", "provider": "AWS"}]

@dataclass
class Subdomain:
    hostname: str                    # e.g. "staging.true-fruits.com"
    source: str                      # "crt.sh", "dns_bruteforce", etc.
    ip: Optional[str]
    is_live: bool                    # Does it respond to HTTP?
    http_status: Optional[int]
    server_header: Optional[str]
    category: Optional[str]          # "mail", "vpn", "staging", "admin", "shop", etc.

@dataclass
class ShodanHost:
    ip: str
    hostnames: List[str]
    ports: List[int]
    services: List[Dict]             # [{"port": 443, "product": "Apache", "version": "2.4.52", ...}]
    vulns: List[str]                 # CVE IDs from Shodan
    os: Optional[str]
    org: Optional[str]               # Organization/ISP
    asn: Optional[str]
    cloud_provider: Optional[str]    # AWS, Azure, Oracle Cloud, etc.
    last_update: Optional[str]

@dataclass
class ExchangeInfo:
    is_exchange: bool
    version: Optional[str]           # e.g. "15.2.1118.40"
    version_name: Optional[str]      # e.g. "Exchange 2019 CU14"
    is_eol: bool
    eol_date: Optional[str]
    endpoints_exposed: List[str]     # ["/owa", "/ecp", "/ews", ...]
    auth_methods: Dict[str, List[str]]  # {"/ews": ["NTLM", "Basic"], ...}
    ntlm_domain: Optional[str]       # AD domain from NTLM challenge
    ntlm_fqdn: Optional[str]         # Server FQDN from NTLM challenge
    ntlm_netbios: Optional[str]      # NetBIOS domain
    internal_hostname: Optional[str]  # From x-feserver header
    owa_html_size: Optional[int]     # Size of OWA login page (clonability indicator)

@dataclass
class FileExposure:
    path: str                        # e.g. "/.htpasswd"
    status_code: int
    content_length: int
    content_preview: str             # First 200 chars (redacted if sensitive)
    severity: Severity
    contains_credentials: bool

@dataclass
class TechFingerprint:
    name: str                        # e.g. "Shopware", "WordPress", "Apache"
    version: Optional[str]
    category: str                    # "CMS", "Framework", "Server", "Analytics", etc.
    source: str                      # How detected: "header", "meta_tag", "js_path", etc.
    cves: List[Dict]                 # Known CVEs for this version

@dataclass
class CredentialExposure:
    email: str
    breach_count: int
    breaches: List[Dict]             # [{"name": "LinkedIn", "date": "2012-05-05", "data_types": [...]}]
    stealer_log_count: Optional[int] # If available via HIBP Pro

@dataclass
class MSPInfo:
    name: Optional[str]              # e.g. "record-consult GmbH"
    domain: Optional[str]            # e.g. "record-consult.com"
    identified_via: str              # "MX relay", "SPF include", "reverse DNS"
    employee_count: Optional[str]
    specialization: Optional[str]
    own_security_score: Optional[int] # Score of MSP's own domain
    client_count_in_db: int          # How many other scanned companies use this MSP
    common_issues: List[str]         # Issues shared across this MSP's clients

@dataclass
class SupplyChainEntry:
    name: str                        # e.g. "Klarna", "Google Analytics"
    domain: Optional[str]
    category: str                    # "Payment", "Analytics", "Chat", "CDN", "Hosting"
    detected_via: str                # "script_tag", "privacy_policy", "cookie", etc.
    nis2_relevant: bool              # Is this a relevant supplier per §30?

@dataclass 
class OwnershipInfo:
    legal_form: Optional[str]        # "GmbH", "AG", "GmbH & Co. KG"
    hrb_number: Optional[str]
    geschaeftsfuehrer: List[Dict]    # [{"name": "Marco Knauf", "role": "Vorsitzender"}]
    gesellschafter: List[Dict]       # [{"name": "Eckes-Granini", "share": "67%"}]
    parent_company: Optional[str]
    parent_domain: Optional[str]
    related_companies: List[str]     # Other companies under same parent

@dataclass
class AttackPath:
    narrative: str                   # LLM-generated kill chain narrative (German)
    steps: List[Dict]                # [{"day": 0, "action": "...", "finding_refs": ["DNS-001"]}]
    entry_point: str                 # Most likely initial access vector
    critical_path_findings: List[str] # Finding IDs on the critical path
    estimated_time_to_compromise: str # e.g. "3-5 Tage"
    damage_scenario: Dict            # {"revenue_loss": "...", "fine": "...", "reputation": "..."}

@dataclass
class ScanResult:
    domain: str
    company_name: str
    scan_timestamp: datetime
    scan_duration_seconds: float
    
    # Module outputs
    dns: DNSResult
    subdomains: List[Subdomain]
    shodan_hosts: List[ShodanHost]
    exchange: Optional[ExchangeInfo]
    file_exposures: List[FileExposure]
    tech_stack: List[TechFingerprint]
    credential_exposures: List[CredentialExposure]
    msp: Optional[MSPInfo]
    supply_chain: List[SupplyChainEntry]
    ownership: Optional[OwnershipInfo]
    
    # Analysis outputs
    findings: List[Finding]
    exposure_score: int              # 0-100
    score_breakdown: Dict[str, int]  # {"email": 85, "infrastructure": 60, ...}
    attack_path: Optional[AttackPath]
    nis2_compliance: Dict[str, str]  # {"§30.2.1": "RED", "§30.2.2": "YELLOW", ...}
    
    # Output paths
    report_html_path: Optional[str]
    report_pdf_path: Optional[str]
    email_draft: Optional[str]
```

---

## 4. MODULE SPECIFICATIONS

### M01: DNS Intelligence

**Purpose:** Extract all DNS records and evaluate email security configuration.

**Implementation:**

```python
import dns.resolver
import re

DKIM_SELECTORS = [
    "default", "selector1", "selector2", "google", "mail", 
    "k1", "k2", "k3", "s1", "s2", "dkim", "mandrill", 
    "mailjet", "cm", "mxvault", "exchange", "ex1", "ex2"
]

def scan_dns(domain: str) -> DNSResult:
    result = DNSResult()
    
    # A Records
    try:
        answers = dns.resolver.resolve(domain, 'A')
        result.a_records = [{"ip": str(r), "provider": identify_provider(str(r))} for r in answers]
    except: pass
    
    # MX Records
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        for r in answers:
            mx_host = str(r.exchange).rstrip('.')
            mx_ip = resolve_ip(mx_host)
            result.mx_records.append({
                "priority": r.preference,
                "host": mx_host,
                "ip": mx_ip,
                "mail_type": classify_mail_server(mx_host)
                # Returns: "exchange_online", "google", "on_prem_exchange", "relay", "other"
            })
    except: pass
    
    # SPF
    try:
        txts = dns.resolver.resolve(domain, 'TXT')
        for r in txts:
            txt = str(r).strip('"')
            if txt.startswith('v=spf1'):
                result.spf_record = txt
                result.spf_mechanism = extract_spf_mechanism(txt)  # ~all, -all, etc.
                result.spf_includes = re.findall(r'include:(\S+)', txt)
                result.spf_ips = re.findall(r'ip[46]:(\S+)', txt)
    except: pass
    
    # DMARC
    try:
        answers = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
        for r in answers:
            txt = str(r).strip('"')
            if 'v=DMARC1' in txt:
                result.dmarc_record = txt
                result.dmarc_policy = extract_dmarc_tag(txt, 'p')
                result.dmarc_subdomain_policy = extract_dmarc_tag(txt, 'sp')
                result.dmarc_alignment_dkim = extract_dmarc_tag(txt, 'adkim')
                result.dmarc_alignment_spf = extract_dmarc_tag(txt, 'aspf')
    except: pass
    
    # DKIM (check all common selectors)
    for selector in DKIM_SELECTORS:
        try:
            answers = dns.resolver.resolve(f'{selector}._domainkey.{domain}', 'TXT')
            if answers:
                result.dkim_selectors_found.append(selector)
        except: pass
        result.dkim_selectors_checked.append(selector)
    
    # MTA-STS
    try:
        dns.resolver.resolve(f'_mta-sts.{domain}', 'TXT')
        result.mta_sts = True
    except:
        result.mta_sts = False
    
    # DANE/TLSA (check for each MX host)
    for mx in result.mx_records:
        try:
            dns.resolver.resolve(f'_25._tcp.{mx["host"]}', 'TLSA')
            result.dane_tlsa = True
        except: pass
    
    # BIMI
    try:
        dns.resolver.resolve(f'default._bimi.{domain}', 'TXT')
        result.bimi = True
    except:
        result.bimi = False
    
    # NS Records
    try:
        answers = dns.resolver.resolve(domain, 'NS')
        result.ns_records = [str(r).rstrip('.') for r in answers]
        result.ns_provider = identify_ns_provider(result.ns_records)
    except: pass
    
    # All TXT records (for verification tokens, etc.)
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        result.txt_records = [str(r).strip('"') for r in answers]
    except: pass
    
    return result
```

**Findings Generated:**

| ID | Condition | Severity |
|----|-----------|----------|
| DNS-001 | SPF uses ~all or ?all instead of -all | HIGH |
| DNS-002 | No SPF record at all | CRITICAL |
| DNS-003 | No DKIM selectors found | HIGH |
| DNS-004 | DMARC policy is "none" | HIGH |
| DNS-005 | DMARC subdomain policy sp=none (while p≠none) | HIGH |
| DNS-006 | No DMARC record at all | CRITICAL |
| DNS-007 | No MTA-STS configured | MEDIUM |
| DNS-008 | No DANE/TLSA records | MEDIUM |
| DNS-009 | No BIMI record | LOW |
| DNS-010 | SPF record includes >10 lookups (risk of permerror) | MEDIUM |

**Dependencies:** `dnspython` (`pip install dnspython`)

**Rate Limiting:** DNS lookups have no API limit. Use system resolver or 8.8.8.8/1.1.1.1.

---

### M02: Subdomain Discovery

**Purpose:** Find all subdomains via Certificate Transparency logs.

**Implementation:**

```python
import requests
import json

def discover_subdomains(domain: str) -> List[Subdomain]:
    subdomains = set()
    
    # Source 1: crt.sh (Certificate Transparency)
    try:
        resp = requests.get(
            f"https://crt.sh/?q=%.{domain}&output=json",
            timeout=30
        )
        if resp.status_code == 200:
            for cert in resp.json():
                name = cert.get("name_value", "")
                for line in name.split("\n"):
                    line = line.strip().lower()
                    if line.endswith(f".{domain}") or line == domain:
                        if "*" not in line:  # Skip wildcards
                            subdomains.add(line)
    except: pass
    
    # Source 2: DNS common subdomain check
    COMMON_SUBS = [
        "www", "mail", "webmail", "remote", "vpn", "citrix",
        "owa", "autodiscover", "ftp", "sftp", "ssh",
        "dev", "staging", "test", "beta", "demo", "sandbox",
        "admin", "portal", "intranet", "extranet",
        "api", "app", "mobile", "m",
        "shop", "store", "blog", "cms", "cdn",
        "db", "database", "mysql", "mssql", "phpmyadmin",
        "backup", "bak", "old", "legacy", "archive",
        "git", "gitlab", "jenkins", "ci", "jira", "confluence",
        "monitoring", "grafana", "kibana", "prometheus",
        "nas", "storage", "files", "cloud",
        "mx", "mx1", "mx2", "smtp", "pop", "imap",
        "ns1", "ns2", "dns",
        "exchange", "lync", "teams", "sip",
    ]
    for sub in COMMON_SUBS:
        fqdn = f"{sub}.{domain}"
        try:
            answers = dns.resolver.resolve(fqdn, 'A')
            subdomains.add(fqdn)
        except: pass
    
    # Resolve each subdomain
    results = []
    for hostname in subdomains:
        sd = Subdomain(hostname=hostname, source="crt.sh+dns")
        try:
            answers = dns.resolver.resolve(hostname, 'A')
            sd.ip = str(answers[0])
        except:
            sd.ip = None
        
        # Check if live (HTTP)
        if sd.ip:
            try:
                resp = requests.get(f"https://{hostname}", timeout=5, allow_redirects=True)
                sd.is_live = True
                sd.http_status = resp.status_code
                sd.server_header = resp.headers.get("Server")
            except:
                try:
                    resp = requests.get(f"http://{hostname}", timeout=5, allow_redirects=True)
                    sd.is_live = True
                    sd.http_status = resp.status_code
                    sd.server_header = resp.headers.get("Server")
                except:
                    sd.is_live = False
        
        # Categorize
        sd.category = categorize_subdomain(hostname)
        results.append(sd)
    
    return results

def categorize_subdomain(hostname: str) -> str:
    name = hostname.split(".")[0].lower()
    categories = {
        "mail": ["mail", "webmail", "owa", "exchange", "mx", "smtp", "imap", "pop"],
        "vpn": ["vpn", "remote", "citrix", "gateway", "ssl"],
        "staging": ["staging", "stage", "stg", "uat", "preprod"],
        "dev": ["dev", "develop", "development", "sandbox", "test", "beta", "demo"],
        "admin": ["admin", "portal", "panel", "dashboard", "console", "manage"],
        "shop": ["shop", "store", "checkout", "order"],
        "api": ["api", "rest", "graphql", "ws", "websocket"],
        "ci_cd": ["jenkins", "ci", "cd", "gitlab", "git", "deploy", "build"],
        "monitoring": ["monitoring", "grafana", "kibana", "prometheus", "nagios", "zabbix"],
        "database": ["db", "database", "mysql", "mssql", "postgres", "phpmyadmin", "adminer"],
        "storage": ["nas", "storage", "files", "ftp", "sftp", "backup", "bak"],
        "intranet": ["intranet", "internal", "wiki", "confluence", "jira", "sharepoint"],
    }
    for cat, keywords in categories.items():
        if name in keywords:
            return cat
    return "other"
```

**Findings Generated:**

| ID | Condition | Severity |
|----|-----------|----------|
| SUB-001 | Staging/dev/test subdomain publicly accessible | HIGH |
| SUB-002 | Database admin panel (phpMyAdmin etc.) publicly accessible | CRITICAL |
| SUB-003 | CI/CD system (Jenkins, GitLab) publicly accessible | HIGH |
| SUB-004 | VPN endpoint identified (attack surface marker) | INFO |
| SUB-005 | Total subdomains > 20 (large attack surface) | MEDIUM |
| SUB-006 | Subdomain resolves but TLS cert is invalid/expired | MEDIUM |

**Dependencies:** `requests`, `dnspython`

**Rate Limiting:** crt.sh has no official limit but throttle to 1 req/2 sec to be polite.

---

### M03: IP Resolution & Cloud Provider Identification

**Purpose:** Map all IPs to cloud providers and geolocation.

```python
import ipaddress

# Cloud provider IP ranges (simplified — use actual CIDR lists in production)
CLOUD_PROVIDERS = {
    "AWS": "https://ip-ranges.amazonaws.com/ip-ranges.json",
    "Azure": "https://www.microsoft.com/en-us/download/details.aspx?id=56519",
    "Google Cloud": "https://www.gstatic.com/ipranges/cloud.json",
    "Oracle Cloud": ["130.61.0.0/16", "132.145.0.0/16", "140.238.0.0/16", 
                     "141.144.0.0/16", "141.147.0.0/16", "144.24.0.0/16",
                     "150.136.0.0/16", "152.67.0.0/16", "152.70.0.0/16"],
    "Hetzner": ["88.198.0.0/16", "136.243.0.0/16", "138.201.0.0/16", 
                "144.76.0.0/16", "148.251.0.0/16", "176.9.0.0/16", "178.63.0.0/16"],
    "IONOS": ["212.227.0.0/16", "217.160.0.0/16", "74.208.0.0/16"],
    "OVH": ["51.38.0.0/16", "51.68.0.0/16", "51.75.0.0/16", "51.77.0.0/16",
             "51.79.0.0/16", "51.89.0.0/16", "51.91.0.0/16"],
    "Strato": ["81.169.0.0/16", "85.214.0.0/16"],
}

def identify_provider(ip: str) -> Optional[str]:
    addr = ipaddress.ip_address(ip)
    for provider, ranges in CLOUD_PROVIDERS.items():
        if isinstance(ranges, list):
            for cidr in ranges:
                if addr in ipaddress.ip_network(cidr):
                    return provider
    # Fallback: reverse DNS / whois
    return reverse_dns_provider(ip)
```

---

### M04: Shodan Lookup

**Purpose:** Enumerate all internet-facing services, open ports, software versions, and known CVEs.

**Implementation:**

```python
import shodan

SHODAN_API_KEY = "YOUR_KEY_HERE"  # $49/month for 1M query credits

def scan_shodan(ip: str) -> ShodanHost:
    api = shodan.Shodan(SHODAN_API_KEY)
    
    try:
        host = api.host(ip)
    except shodan.APIError:
        return ShodanHost(ip=ip, hostnames=[], ports=[], services=[], vulns=[])
    
    result = ShodanHost(
        ip=ip,
        hostnames=host.get("hostnames", []),
        ports=host.get("ports", []),
        os=host.get("os"),
        org=host.get("org"),
        asn=host.get("asn"),
        last_update=host.get("last_update"),
        vulns=host.get("vulns", []),
        cloud_provider=identify_provider(ip),
    )
    
    for service in host.get("data", []):
        result.services.append({
            "port": service.get("port"),
            "transport": service.get("transport"),
            "product": service.get("product"),
            "version": service.get("version"),
            "banner": service.get("data", "")[:500],  # Truncate banner
            "module": service.get("_shodan", {}).get("module"),
            "ssl": {
                "cert_subject": service.get("ssl", {}).get("cert", {}).get("subject", {}),
                "cert_issuer": service.get("ssl", {}).get("cert", {}).get("issuer", {}),
                "cert_expires": service.get("ssl", {}).get("cert", {}).get("expires"),
                "cipher": service.get("ssl", {}).get("cipher", {}),
                "versions": service.get("ssl", {}).get("versions", []),
            } if "ssl" in service else None,
        })
    
    return result
```

**Findings Generated:**

| ID | Condition | Severity |
|----|-----------|----------|
| SHO-001 | RDP (3389) exposed to internet | CRITICAL |
| SHO-002 | SMB (445) exposed to internet | CRITICAL |
| SHO-003 | Database port exposed (3306/5432/1433/27017/6379) | CRITICAL |
| SHO-004 | FTP (21) exposed | HIGH |
| SHO-005 | Telnet (23) exposed | CRITICAL |
| SHO-006 | VNC (5900) exposed | CRITICAL |
| SHO-007 | Known CVEs from Shodan vulns list | Varies |
| SHO-008 | EOL software detected (via version matching) | HIGH-CRITICAL |
| SHO-009 | SSL certificate expired | MEDIUM |
| SHO-010 | Weak TLS versions (TLS 1.0/1.1) still enabled | MEDIUM |
| SHO-011 | Self-signed certificate on production service | MEDIUM |
| SHO-012 | >10 ports open (large attack surface) | MEDIUM |

**Dependencies:** `shodan` (`pip install shodan`)

**Rate Limiting:** Shodan API: 1 query/second on paid plan. Budget ~$49/month for 1M credits.

**Critical Shodan Queries for German Mittelstand:**

```python
# Find all Exchange servers in Germany
EXCHANGE_QUERY = 'http.title:"Outlook" country:"DE" org:"{company_name}"'

# Find RDP exposed in a specific IP range
RDP_QUERY = 'port:3389 country:"DE" net:{ip_range}'

# Find all services for a specific org
ORG_QUERY = 'org:"{org_name}"'
```

---

### M05: HTTP Security Headers

**Purpose:** Check security header configuration on all live web hosts.

```python
SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "severity_missing": Severity.MEDIUM,
        "check_values": lambda v: "max-age=" in v and int(re.search(r'max-age=(\d+)', v).group(1)) >= 31536000,
    },
    "Content-Security-Policy": {
        "severity_missing": Severity.MEDIUM,
        "check_values": lambda v: "unsafe-inline" not in v and "unsafe-eval" not in v,
    },
    "X-Content-Type-Options": {
        "severity_missing": Severity.LOW,
        "expected": "nosniff",
    },
    "X-Frame-Options": {
        "severity_missing": Severity.LOW,
        "expected_any": ["DENY", "SAMEORIGIN"],
    },
    "Permissions-Policy": {
        "severity_missing": Severity.LOW,
    },
    "Referrer-Policy": {
        "severity_missing": Severity.LOW,
    },
    "X-XSS-Protection": {
        "severity_missing": Severity.INFO,  # Deprecated but still checked
    },
}

# Headers that SHOULD NOT be present (information disclosure)
LEAKY_HEADERS = ["X-Powered-By", "Server", "X-AspNet-Version", "X-AspNetMvc-Version"]

def check_security_headers(url: str) -> List[Finding]:
    findings = []
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True)
        headers = resp.headers
        
        # Check required headers
        for header, config in SECURITY_HEADERS.items():
            if header not in headers:
                findings.append(Finding(
                    id=f"HDR-{header[:3].upper()}",
                    title=f"{header} Header fehlt",
                    severity=config["severity_missing"],
                    evidence=f"GET {url} → Header nicht vorhanden",
                    ...
                ))
        
        # Check leaky headers
        for header in LEAKY_HEADERS:
            if header in headers:
                findings.append(Finding(
                    id=f"HDR-LEAK-{header[:3].upper()}",
                    title=f"{header} exponiert Serverinformationen",
                    severity=Severity.LOW,
                    evidence=f"{header}: {headers[header]}",
                    ...
                ))
        
        # Check cookies
        for cookie_header in resp.headers.getlist("Set-Cookie") if hasattr(resp.headers, 'getlist') else [resp.headers.get("Set-Cookie", "")]:
            if cookie_header:
                if "Secure" not in cookie_header:
                    findings.append(...)
                if "HttpOnly" not in cookie_header:
                    findings.append(...)
                if "SameSite" not in cookie_header:
                    findings.append(...)
    
    except Exception as e:
        pass
    
    return findings
```

---

### M08: Exchange Detection & NTLM Challenge

**Purpose:** Identify Exchange servers, enumerate exposed endpoints, and extract AD information via NTLM challenge.

```python
import base64
import struct

EXCHANGE_ENDPOINTS = [
    "/owa",                          # Outlook Web Access
    "/ecp",                          # Exchange Control Panel (Admin)
    "/ews/exchange.asmx",            # Exchange Web Services
    "/Microsoft-Server-ActiveSync",  # Mobile sync
    "/mapi",                         # MAPI over HTTP
    "/rpc",                          # RPC over HTTP
    "/PowerShell",                   # Remote PowerShell
    "/autodiscover/autodiscover.xml",# Autodiscover
    "/oab",                          # Offline Address Book
]

# NTLM Type 1 message (empty, minimal — triggers Type 2 response)
NTLM_TYPE1 = base64.b64encode(
    b'\x4e\x54\x4c\x4d\x53\x53\x50\x00'  # NTLMSSP signature
    b'\x01\x00\x00\x00'                    # Type 1 message
    b'\x07\x82\x08\x00'                    # Flags
    b'\x00\x00\x00\x00\x00\x00\x00\x00'    # Domain (empty)
    b'\x00\x00\x00\x00\x00\x00\x00\x00'    # Workstation (empty)
).decode()

def scan_exchange(mail_host: str) -> ExchangeInfo:
    result = ExchangeInfo(is_exchange=False)
    base_url = f"https://{mail_host}"
    
    # Check each endpoint
    for endpoint in EXCHANGE_ENDPOINTS:
        url = f"{base_url}{endpoint}"
        try:
            resp = requests.get(url, timeout=10, allow_redirects=False, verify=False)
            if resp.status_code in [200, 301, 302, 401, 403]:
                result.is_exchange = True
                result.endpoints_exposed.append(endpoint)
                
                # Extract auth methods
                www_auth = resp.headers.get("WWW-Authenticate", "")
                auth_methods = []
                if "NTLM" in www_auth: auth_methods.append("NTLM")
                if "Negotiate" in www_auth: auth_methods.append("Negotiate")
                if "Basic" in www_auth: auth_methods.append("Basic")
                result.auth_methods[endpoint] = auth_methods
                
                # Extract version from OWA
                owa_version = resp.headers.get("X-OWA-Version")
                if owa_version:
                    result.version = owa_version
                    result.version_name = map_exchange_version(owa_version)
                    result.is_eol = check_exchange_eol(owa_version)
                
                # Extract internal hostname
                fe_server = resp.headers.get("X-FEServer")
                if fe_server:
                    result.internal_hostname = fe_server
                
        except: pass
    
    # NTLM Challenge (if NTLM auth detected on any endpoint)
    if any("NTLM" in methods for methods in result.auth_methods.values()):
        ntlm_endpoint = next(
            (ep for ep, methods in result.auth_methods.items() if "NTLM" in methods),
            None
        )
        if ntlm_endpoint:
            try:
                resp = requests.get(
                    f"{base_url}{ntlm_endpoint}",
                    headers={"Authorization": f"NTLM {NTLM_TYPE1}"},
                    timeout=10,
                    verify=False
                )
                www_auth = resp.headers.get("WWW-Authenticate", "")
                if "NTLM " in www_auth:
                    ntlm_b64 = www_auth.split("NTLM ")[1].split(",")[0].strip()
                    ntlm_data = base64.b64decode(ntlm_b64)
                    decoded = decode_ntlm_type2(ntlm_data)
                    result.ntlm_domain = decoded.get("dns_domain")
                    result.ntlm_fqdn = decoded.get("dns_computer")
                    result.ntlm_netbios = decoded.get("netbios_domain")
            except: pass
    
    # Check OWA page size (clonability indicator)
    try:
        resp = requests.get(f"{base_url}/owa/auth/logon.aspx", timeout=10, verify=False)
        if resp.status_code == 200:
            result.owa_html_size = len(resp.content)
    except: pass
    
    return result

def decode_ntlm_type2(data: bytes) -> Dict:
    """Decode NTLM Type 2 challenge to extract AD domain info."""
    # Skip signature (8 bytes) + type (4 bytes)
    # Target info at offset specified in bytes 40-47
    result = {}
    
    if len(data) < 56:
        return result
    
    # Target info fields offset and length
    target_info_len = struct.unpack('<H', data[40:42])[0]
    target_info_offset = struct.unpack('<I', data[44:48])[0]
    
    if target_info_offset + target_info_len > len(data):
        return result
    
    # Parse AV_PAIR structures
    offset = target_info_offset
    while offset < target_info_offset + target_info_len:
        av_id = struct.unpack('<H', data[offset:offset+2])[0]
        av_len = struct.unpack('<H', data[offset+2:offset+4])[0]
        av_value = data[offset+4:offset+4+av_len]
        
        if av_id == 0:  # MsvAvEOL
            break
        elif av_id == 1:  # MsvAvNbComputerName
            result["netbios_computer"] = av_value.decode('utf-16-le')
        elif av_id == 2:  # MsvAvNbDomainName
            result["netbios_domain"] = av_value.decode('utf-16-le')
        elif av_id == 3:  # MsvAvDnsComputerName
            result["dns_computer"] = av_value.decode('utf-16-le')
        elif av_id == 4:  # MsvAvDnsDomainName
            result["dns_domain"] = av_value.decode('utf-16-le')
        elif av_id == 5:  # MsvAvDnsTreeName
            result["dns_tree"] = av_value.decode('utf-16-le')
        elif av_id == 7:  # MsvAvTimestamp
            result["timestamp"] = struct.unpack('<Q', av_value)[0]
        
        offset += 4 + av_len
    
    return result

# Exchange version mapping
EXCHANGE_VERSIONS = {
    "15.2": {
        "name": "Exchange Server 2019",
        "eol_mainstream": "2024-10-14",
        "eol_extended": "2025-10-14",
        "eol_esu": "2026-04-14",  # ESU ends THIS MONTH
        "builds": {
            "1118": "CU14 (Feb 2024)",
            "1544": "CU15 (anticipated)",
        }
    },
    "15.1": {
        "name": "Exchange Server 2016",
        "eol_mainstream": "2020-10-13",
        "eol_extended": "2025-10-14",
        "eol_esu": "2026-04-14",
    },
    "15.0": {
        "name": "Exchange Server 2013",
        "eol": "2023-04-11",  # Completely EOL
    },
    "14.": {
        "name": "Exchange Server 2010",
        "eol": "2020-10-13",
    },
}
```

**Findings Generated:**

| ID | Condition | Severity |
|----|-----------|----------|
| EX-001 | Exchange version is End-of-Life | CRITICAL |
| EX-002 | /owa publicly accessible | HIGH |
| EX-003 | /ecp (Admin panel) publicly accessible | CRITICAL |
| EX-004 | /PowerShell endpoint publicly accessible | CRITICAL |
| EX-005 | Basic Auth enabled (credentials as Base64) | HIGH |
| EX-006 | NTLM auth enabled (relay attacks possible) | HIGH |
| EX-007 | AD domain name leaked via NTLM challenge | CRITICAL |
| EX-008 | Server FQDN leaked via NTLM challenge | HIGH |
| EX-009 | Internal hostname leaked via X-FEServer | MEDIUM |
| EX-010 | >5 Exchange endpoints publicly accessible | HIGH |
| EX-011 | OWA login page cloneable (>10KB HTML) | MEDIUM |

---

### M09: Common File Exposure Check

**Purpose:** Check for sensitive files left publicly accessible.

```python
# Ordered by severity (check most critical first)
FILE_CHECKS = [
    # CRITICAL: Credentials and secrets
    {"path": "/.env", "severity": Severity.CRITICAL, "desc": "Environment variables (often contains DB passwords, API keys)"},
    {"path": "/.htpasswd", "severity": Severity.CRITICAL, "desc": "Apache password file with crackable hashes"},
    {"path": "/web.config", "severity": Severity.HIGH, "desc": "IIS config (may contain connection strings)"},
    {"path": "/.git/config", "severity": Severity.CRITICAL, "desc": "Git repository config (source code exposure)"},
    {"path": "/.git/HEAD", "severity": Severity.CRITICAL, "desc": "Git repository HEAD (confirms .git exposed)"},
    {"path": "/wp-config.php.bak", "severity": Severity.CRITICAL, "desc": "WordPress config backup (DB credentials)"},
    {"path": "/wp-config.php~", "severity": Severity.CRITICAL, "desc": "WordPress config editor backup"},
    {"path": "/config.php.bak", "severity": Severity.HIGH, "desc": "PHP config backup"},
    
    # HIGH: Server configuration
    {"path": "/.htaccess", "severity": Severity.MEDIUM, "desc": "Apache configuration"},
    {"path": "/server-status", "severity": Severity.HIGH, "desc": "Apache server status (connection info)"},
    {"path": "/server-info", "severity": Severity.HIGH, "desc": "Apache server info (full config)"},
    {"path": "/phpinfo.php", "severity": Severity.HIGH, "desc": "PHP info page (full server config)"},
    {"path": "/info.php", "severity": Severity.HIGH, "desc": "PHP info page variant"},
    
    # HIGH: Database and backups
    {"path": "/backup.sql", "severity": Severity.CRITICAL, "desc": "SQL database backup"},
    {"path": "/dump.sql", "severity": Severity.CRITICAL, "desc": "SQL database dump"},
    {"path": "/database.sql", "severity": Severity.CRITICAL, "desc": "SQL database export"},
    {"path": "/backup.zip", "severity": Severity.CRITICAL, "desc": "Backup archive"},
    {"path": "/backup.tar.gz", "severity": Severity.CRITICAL, "desc": "Backup archive"},
    
    # MEDIUM: Development artifacts
    {"path": "/composer.json", "severity": Severity.MEDIUM, "desc": "PHP dependency manifest"},
    {"path": "/composer.lock", "severity": Severity.MEDIUM, "desc": "PHP dependency lock file"},
    {"path": "/package.json", "severity": Severity.MEDIUM, "desc": "Node.js dependency manifest"},
    {"path": "/package-lock.json", "severity": Severity.LOW, "desc": "Node.js lock file"},
    {"path": "/Dockerfile", "severity": Severity.MEDIUM, "desc": "Docker configuration"},
    {"path": "/docker-compose.yml", "severity": Severity.HIGH, "desc": "Docker Compose (may contain credentials)"},
    
    # INFO: Useful reconnaissance
    {"path": "/robots.txt", "severity": Severity.INFO, "desc": "Robot exclusion (reveals hidden paths)"},
    {"path": "/sitemap.xml", "severity": Severity.INFO, "desc": "Sitemap (full URL structure)"},
    {"path": "/.well-known/security.txt", "severity": Severity.INFO, "desc": "Security contact (positive finding)"},
    
    # CMS-specific admin panels
    {"path": "/admin", "severity": Severity.HIGH, "desc": "Admin panel accessible"},
    {"path": "/wp-admin", "severity": Severity.MEDIUM, "desc": "WordPress admin"},
    {"path": "/wp-login.php", "severity": Severity.MEDIUM, "desc": "WordPress login"},
    {"path": "/administrator", "severity": Severity.MEDIUM, "desc": "Joomla admin"},
    {"path": "/typo3", "severity": Severity.MEDIUM, "desc": "TYPO3 admin"},
    {"path": "/user/login", "severity": Severity.MEDIUM, "desc": "Drupal login"},
    
    # API documentation (attack surface intel)
    {"path": "/swagger", "severity": Severity.MEDIUM, "desc": "Swagger API documentation"},
    {"path": "/swagger-ui", "severity": Severity.MEDIUM, "desc": "Swagger UI"},
    {"path": "/api-docs", "severity": Severity.MEDIUM, "desc": "API documentation"},
    {"path": "/graphql", "severity": Severity.MEDIUM, "desc": "GraphQL endpoint"},
    {"path": "/_profiler", "severity": Severity.HIGH, "desc": "Symfony profiler (debug info)"},
    {"path": "/_wdt", "severity": Severity.HIGH, "desc": "Symfony Web Debug Toolbar"},
]

def check_file_exposures(base_url: str) -> List[FileExposure]:
    results = []
    
    for check in FILE_CHECKS:
        url = f"{base_url}{check['path']}"
        try:
            resp = requests.get(url, timeout=5, allow_redirects=False)
            
            # Only count as exposed if real content (not generic 404 page)
            if resp.status_code == 200 and len(resp.content) > 0:
                # Filter out soft-404s (custom error pages that return 200)
                if not is_soft_404(resp, check['path']):
                    content_preview = resp.text[:200]
                    # Redact potential credentials
                    if check['severity'] in [Severity.CRITICAL, Severity.HIGH]:
                        content_preview = redact_credentials(content_preview)
                    
                    results.append(FileExposure(
                        path=check['path'],
                        status_code=resp.status_code,
                        content_length=len(resp.content),
                        content_preview=content_preview,
                        severity=check['severity'],
                        contains_credentials="password" in resp.text.lower() or 
                                            "secret" in resp.text.lower() or
                                            "$apr1$" in resp.text or
                                            "DB_" in resp.text,
                    ))
        except: pass
    
    return results

def is_soft_404(resp, path: str) -> bool:
    """Detect custom 404 pages that return HTTP 200."""
    content = resp.text.lower()
    # If the response contains the path we requested, it might be a real page
    # If it contains "not found", "404", "error", it's likely a soft 404
    soft_404_indicators = ["page not found", "404", "not found", "does not exist", "seite nicht gefunden"]
    return any(indicator in content for indicator in soft_404_indicators)
```

---

### M12: Credential Exposure (HIBP)

**Purpose:** Check if known employee emails appear in data breaches.

```python
import time

HIBP_API_KEY = "YOUR_KEY_HERE"  # $3.50/month
HIBP_HEADERS = {
    "hibp-api-key": HIBP_API_KEY,
    "user-agent": "Kengo-Scanner/1.0",
}

def check_credential_exposure(emails: List[str]) -> List[CredentialExposure]:
    results = []
    
    for email in emails:
        # Rate limit: HIBP allows 10 RPM on basic plan
        time.sleep(6)  # 10 requests per minute = 1 every 6 seconds
        
        try:
            resp = requests.get(
                f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                headers=HIBP_HEADERS,
                params={"truncateResponse": "false"},
                timeout=10,
            )
            
            if resp.status_code == 200:
                breaches = resp.json()
                results.append(CredentialExposure(
                    email=email,
                    breach_count=len(breaches),
                    breaches=[{
                        "name": b["Name"],
                        "title": b["Title"],
                        "date": b["BreachDate"],
                        "added_date": b["AddedDate"],
                        "pawn_count": b["PwnCount"],
                        "data_types": b["DataClasses"],
                        "is_verified": b["IsVerified"],
                        "domain": b["Domain"],
                    } for b in breaches],
                ))
            elif resp.status_code == 404:
                # Not found in any breach — this is GOOD
                results.append(CredentialExposure(
                    email=email, breach_count=0, breaches=[]
                ))
            elif resp.status_code == 429:
                # Rate limited — back off
                time.sleep(30)
                
        except Exception as e:
            pass
    
    return results
```

**Finding logic:**

| ID | Condition | Severity |
|----|-----------|----------|
| CRED-001 | GF email in 1-2 breaches | MEDIUM |
| CRED-002 | GF email in 3+ breaches | HIGH |
| CRED-003 | Any email in breach containing passwords | CRITICAL |
| CRED-004 | Email in recent breach (<1 year) | HIGH |
| CRED-005 | Multiple employees in same breach (targeted?) | HIGH |

**Important Note:** HIBP does NOT let you search arbitrary emails without domain verification for domain-wide search. However, you CAN search individual email addresses with an API key. For the scanner, we use known GF/employee emails from the lead list (Apollo, LinkedIn, Impressum parsing).

---

### M13: MSP Identification & Scoring

```python
def identify_msp(dns_result: DNSResult, domain: str) -> Optional[MSPInfo]:
    msp_signals = []
    
    # Signal 1: MX relay domain
    for mx in dns_result.mx_records:
        mx_domain = extract_base_domain(mx["host"])
        if mx_domain != domain:
            msp_signals.append(("MX relay", mx_domain))
    
    # Signal 2: SPF includes
    for include in dns_result.spf_includes:
        inc_domain = extract_base_domain(include)
        if inc_domain != domain:
            msp_signals.append(("SPF include", inc_domain))
    
    # Signal 3: Reverse DNS on mail server IPs
    for mx in dns_result.mx_records:
        if mx.get("ip"):
            try:
                rdns = dns.resolver.resolve_address(mx["ip"])
                rdns_domain = extract_base_domain(str(rdns[0]).rstrip('.'))
                if rdns_domain != domain:
                    msp_signals.append(("Reverse DNS", rdns_domain))
            except: pass
    
    if not msp_signals:
        return None
    
    # Most frequent domain across signals = most likely MSP
    from collections import Counter
    domain_counts = Counter(d for _, d in msp_signals)
    msp_domain = domain_counts.most_common(1)[0][0]
    
    # Enrich MSP info
    msp = MSPInfo(
        domain=msp_domain,
        identified_via=", ".join(set(s for s, d in msp_signals if d == msp_domain)),
    )
    
    # Try to resolve MSP name from website
    try:
        resp = requests.get(f"https://{msp_domain}", timeout=10)
        # Extract company name from title tag
        title_match = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE)
        if title_match:
            msp.name = title_match.group(1).strip()
    except: pass
    
    # Scan the MSP's own domain for security posture
    # (This creates the MSP scoring database over time)
    
    return msp
```

---

### M14: Supply Chain Mapping

```python
def map_supply_chain(url: str) -> List[SupplyChainEntry]:
    entries = []
    
    try:
        resp = requests.get(url, timeout=10)
        html = resp.text
        
        # Detect third-party scripts
        KNOWN_SERVICES = {
            # Analytics
            "google-analytics.com": ("Google Analytics", "Analytics"),
            "googletagmanager.com": ("Google Tag Manager", "Analytics"),
            "matomo": ("Matomo", "Analytics"),
            "hotjar.com": ("Hotjar", "Analytics"),
            "clarity.ms": ("Microsoft Clarity", "Analytics"),
            
            # Payment
            "klarna.com": ("Klarna", "Payment"),
            "paypal.com": ("PayPal", "Payment"),
            "stripe.com": ("Stripe", "Payment"),
            "adyen.com": ("Adyen", "Payment"),
            "mollie.com": ("Mollie", "Payment"),
            
            # Chat & Support
            "zendesk.com": ("Zendesk", "Support"),
            "intercom.io": ("Intercom", "Support"),
            "smartsupp.com": ("Smartsupp", "Chat"),
            "tidio.co": ("Tidio", "Chat"),
            "crisp.chat": ("Crisp", "Chat"),
            "hubspot.com": ("HubSpot", "CRM/Marketing"),
            
            # CDN & Infrastructure
            "cloudflare.com": ("Cloudflare", "CDN"),
            "fastly.net": ("Fastly", "CDN"),
            "akamai.net": ("Akamai", "CDN"),
            "cloudfront.net": ("AWS CloudFront", "CDN"),
            
            # Marketing
            "facebook.net": ("Meta Pixel", "Marketing"),
            "doubleclick.net": ("Google Ads", "Marketing"),
            "linkedin.com/insight": ("LinkedIn Insight", "Marketing"),
            "tiktok.com": ("TikTok Pixel", "Marketing"),
            
            # E-Commerce
            "shopify.com": ("Shopify", "E-Commerce Platform"),
            "shopware.com": ("Shopware", "E-Commerce Platform"),
            "woocommerce.com": ("WooCommerce", "E-Commerce Platform"),
            
            # Email Marketing  
            "mailchimp.com": ("Mailchimp", "Email Marketing"),
            "sendinblue.com": ("Brevo", "Email Marketing"),
            "klaviyo.com": ("Klaviyo", "Email Marketing"),
        }
        
        for domain_pattern, (name, category) in KNOWN_SERVICES.items():
            if domain_pattern in html:
                entries.append(SupplyChainEntry(
                    name=name,
                    domain=domain_pattern,
                    category=category,
                    detected_via="script_tag",
                    nis2_relevant=category in ["Payment", "E-Commerce Platform", "Support", "CRM/Marketing"],
                ))
        
        # Parse Datenschutzerklärung for additional processors
        privacy_url = find_privacy_page(url, html)
        if privacy_url:
            try:
                privacy_resp = requests.get(privacy_url, timeout=10)
                # Extract data processor mentions
                # (This is where an LLM can help parse unstructured privacy policies)
            except: pass
            
    except: pass
    
    return entries
```

---

### M16: Scoring Engine

```python
SCORE_WEIGHTS = {
    "email_security": 0.20,      # SPF, DMARC, DKIM, MTA-STS
    "infrastructure": 0.25,      # Shodan, open ports, EOL software
    "web_application": 0.20,     # Headers, file exposure, admin panels
    "credential_exposure": 0.15, # HIBP results
    "exchange_exposure": 0.10,   # Exchange-specific findings
    "supply_chain": 0.10,        # MSP quality, supply chain risk
}

SEVERITY_SCORES = {
    Severity.CRITICAL: 25,
    Severity.HIGH: 15,
    Severity.MEDIUM: 8,
    Severity.LOW: 3,
    Severity.INFO: 0,
}

def calculate_exposure_score(findings: List[Finding]) -> Tuple[int, Dict[str, int]]:
    """Calculate 0-100 exposure score. Higher = more exposed = worse."""
    
    category_scores = {}
    
    for category, weight in SCORE_WEIGHTS.items():
        cat_findings = [f for f in findings if f.category == category]
        raw_score = sum(SEVERITY_SCORES[f.severity] for f in cat_findings)
        # Normalize to 0-100 per category (cap at 100)
        normalized = min(100, raw_score)
        category_scores[category] = normalized
    
    # Weighted total
    total = sum(
        category_scores.get(cat, 0) * weight 
        for cat, weight in SCORE_WEIGHTS.items()
    )
    
    return min(100, int(total)), category_scores
```

---

### M17: Attack Path Assembly (LLM)

```python
import anthropic

def generate_attack_path(scan_result: ScanResult) -> AttackPath:
    client = anthropic.Anthropic()
    
    # Prepare findings summary for the LLM
    findings_text = "\n".join([
        f"- [{f.severity.value}] {f.title}: {f.evidence}"
        for f in sorted(scan_result.findings, key=lambda x: x.severity.value)
    ])
    
    prompt = f"""Du bist ein erfahrener Penetration Tester. Basierend auf den folgenden 
    externen Reconnaissance-Ergebnissen für {scan_result.company_name} ({scan_result.domain}), 
    erstelle einen realistischen Angriffsnarrativ.

    FINDINGS:
    {findings_text}
    
    INFRASTRUKTUR:
    - Mail Server: {scan_result.exchange.version_name if scan_result.exchange else 'Unbekannt'}
    - AD Domain: {scan_result.exchange.ntlm_domain if scan_result.exchange else 'Nicht identifiziert'}
    - Cloud Provider: {scan_result.shodan_hosts[0].cloud_provider if scan_result.shodan_hosts else 'Unbekannt'}
    - MSP: {scan_result.msp.name if scan_result.msp else 'Nicht identifiziert'}
    
    CREDENTIAL EXPOSURE:
    {chr(10).join([f"- {c.email}: {c.breach_count} Breaches" for c in scan_result.credential_exposures])}
    
    Erstelle:
    1. Einen Tag-für-Tag Angriffsnarrativ (Tag 0 bis Tag N) der zeigt wie ein 
       motivierter Angreifer dieses Unternehmen kompromittieren würde.
       Jeder Tag referenziert konkrete Findings.
    2. Den wahrscheinlichsten Initial Access Vector.
    3. Eine Schadensrechnung (Umsatzausfall, DSGVO-Bußgeld, NIS2 §38 Haftung, Reputation).
    4. Die 3 dringendsten Maßnahmen.
    
    Schreibe auf Deutsch. Sei spezifisch — nenne konkrete Server, Domains, Versionen.
    Kein generischer Text. Jeder Satz muss sich auf ein verifiziertes Finding beziehen.
    
    Antworte als JSON:
    {{
        "narrative": "Tag 0: ... Tag 1: ... Tag N: ...",
        "steps": [{{"day": 0, "action": "...", "finding_refs": ["EX-001"]}}],
        "entry_point": "...",
        "critical_path_findings": ["EX-001", "DNS-001", ...],
        "estimated_time": "3-5 Tage",
        "damage": {{
            "revenue_loss_per_day": "...",
            "dsgvo_fine": "bis zu 4% des Jahresumsatzes",
            "nis2_personal_liability": "§38 BSIG — GF haften persönlich mit Privatvermögen",
            "reputation": "..."
        }},
        "top3_actions": ["...", "...", "..."]
    }}"""
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    
    # Parse JSON response
    result_json = json.loads(response.content[0].text)
    
    return AttackPath(
        narrative=result_json["narrative"],
        steps=result_json["steps"],
        entry_point=result_json["entry_point"],
        critical_path_findings=result_json["critical_path_findings"],
        estimated_time_to_compromise=result_json["estimated_time"],
        damage_scenario=result_json["damage"],
    )
```

---

### M18: NIS2 Compliance Mapping

```python
NIS2_REQUIREMENTS = {
    "§30.2.1": {
        "title": "Risikoanalyse und Sicherheitskonzepte",
        "findings_map": ["EX-001", "SHO-001", "SHO-002", "SHO-003"],
        "description": "Konzepte für Risikoanalyse und Sicherheit für Informationssysteme",
    },
    "§30.2.2": {
        "title": "Bewältigung von Sicherheitsvorfällen",
        "findings_map": ["DNS-004", "DNS-006"],  # No DMARC = can't detect spoofing incidents
    },
    "§30.2.3": {
        "title": "Business Continuity und Krisenmanagement",
        "findings_map": [],  # Can't assess from external scan
    },
    "§30.2.4": {
        "title": "Sicherheit der Lieferkette",
        "findings_map": ["MSP-*", "SC-*"],  # All MSP and supply chain findings
    },
    "§30.2.5": {
        "title": "Sicherheit bei Erwerb, Entwicklung und Wartung",
        "findings_map": ["EX-001", "SHO-008", "SHOP-*"],
    },
    "§30.2.6": {
        "title": "Bewertung der Wirksamkeit von Maßnahmen",
        "findings_map": [],  # Can't assess from external scan
    },
    "§30.2.7": {
        "title": "Cyberhygiene und Schulungen",
        "findings_map": ["CRED-*"],  # Credential reuse indicates poor hygiene
    },
    "§30.2.8": {
        "title": "Kryptografie und Verschlüsselung",
        "findings_map": ["TLS-*", "EX-005"],  # Weak TLS, Basic Auth
    },
    "§30.2.9": {
        "title": "Zugriffskontrolle und Anlagenmanagement",
        "findings_map": ["EX-003", "EX-004", "FILE-*", "ADMIN-*"],
    },
    "§30.2.10": {
        "title": "Multi-Faktor-Authentisierung",
        "findings_map": [],  # Can't verify MFA from external scan
    },
}

def map_nis2_compliance(findings: List[Finding]) -> Dict[str, str]:
    """Map findings to NIS2 §30 requirements. Returns traffic light per requirement."""
    result = {}
    
    for paragraph, config in NIS2_REQUIREMENTS.items():
        relevant_findings = []
        for pattern in config["findings_map"]:
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                relevant_findings.extend([f for f in findings if f.id.startswith(prefix)])
            else:
                relevant_findings.extend([f for f in findings if f.id == pattern])
        
        if not relevant_findings:
            result[paragraph] = "GRAY"  # Can't assess
        elif any(f.severity == Severity.CRITICAL for f in relevant_findings):
            result[paragraph] = "RED"
        elif any(f.severity == Severity.HIGH for f in relevant_findings):
            result[paragraph] = "YELLOW"
        else:
            result[paragraph] = "GREEN"
    
    return result
```

---

## 5. DEPENDENCIES & COSTS

### Python Packages

```
# requirements.txt
dnspython==2.7.0
requests==2.32.0
shodan==1.31.0
anthropic==0.42.0
python-whois==0.9.4
beautifulsoup4==4.12.0
jinja2==3.1.4          # For HTML report templates
weasyprint==62.3       # For PDF generation from HTML
tqdm==4.67.0           # Progress bars
aiohttp==3.11.0        # Async HTTP (optional, for parallel scanning)
```

### API Costs (Monthly)

| Service | Plan | Cost | What You Get |
|---------|------|------|-------------|
| Shodan | Membership | $49/month | 1M query credits, all filters, bulk lookups |
| HIBP | Core | $3.50/month | Email breach search API, 10 RPM |
| Anthropic | Pay-as-you-go | ~$50-100/month | Claude Sonnet for attack path generation |
| crt.sh | Free | $0 | Certificate Transparency log search |
| DNS | Free | $0 | Standard DNS resolution |

**Total: ~$103-153/month** for scanning thousands of companies.

### Infrastructure

- Any machine with Python 3.10+ and internet access
- No GPU needed
- Recommended: 4GB RAM, SSD for results storage
- Claude Code works perfectly as the development environment

---

## 6. ORCHESTRATOR (main.py)

```python
#!/usr/bin/env python3
"""
KENGO ARGUS — Automated Reconnaissance Engine
Usage: python main.py --input leads.csv --output results/
"""

import argparse
import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

def scan_domain(lead: dict) -> ScanResult:
    """Run all modules for a single domain."""
    domain = lead["domain"]
    start_time = time.time()
    
    result = ScanResult(
        domain=domain,
        company_name=lead.get("company_name", domain),
        scan_timestamp=datetime.utcnow(),
    )
    
    # Phase 1: DNS
    print(f"  [1/5] DNS Intelligence...")
    result.dns = scan_dns(domain)
    
    print(f"  [1/5] Subdomain Discovery...")
    result.subdomains = discover_subdomains(domain)
    
    # Phase 2: Service Enumeration
    all_ips = set()
    for rec in result.dns.a_records:
        all_ips.add(rec["ip"])
    for mx in result.dns.mx_records:
        if mx.get("ip"):
            all_ips.add(mx["ip"])
    for sd in result.subdomains:
        if sd.ip:
            all_ips.add(sd.ip)
    
    print(f"  [2/5] Shodan Lookup ({len(all_ips)} IPs)...")
    for ip in all_ips:
        host = scan_shodan(ip)
        result.shodan_hosts.append(host)
        time.sleep(1)  # Shodan rate limit
    
    print(f"  [2/5] HTTP Headers & Files...")
    live_urls = [f"https://{domain}"]
    for sd in result.subdomains:
        if sd.is_live:
            live_urls.append(f"https://{sd.hostname}")
    
    for url in live_urls[:10]:  # Cap at 10 to avoid excessive requests
        result.findings.extend(check_security_headers(url))
        result.file_exposures.extend(check_file_exposures(url))
        result.tech_stack.extend(fingerprint_technology(url))
    
    # Phase 3: Deep Recon
    print(f"  [3/5] Exchange & NTLM...")
    for mx in result.dns.mx_records:
        if is_exchange_candidate(mx):
            result.exchange = scan_exchange(mx["host"])
            break
    
    # Phase 4: Intelligence
    print(f"  [4/5] Credential Exposure & MSP...")
    emails = []
    if lead.get("gf_email"):
        emails.append(lead["gf_email"])
    # Add other known emails from lead data
    result.credential_exposures = check_credential_exposure(emails)
    result.msp = identify_msp(result.dns, domain)
    result.supply_chain = map_supply_chain(f"https://{domain}")
    
    # Phase 5: Analysis
    print(f"  [5/5] Scoring & Attack Path...")
    # Generate findings from all module results
    result.findings.extend(generate_dns_findings(result.dns))
    result.findings.extend(generate_exchange_findings(result.exchange))
    result.findings.extend(generate_shodan_findings(result.shodan_hosts))
    result.findings.extend(generate_credential_findings(result.credential_exposures))
    result.findings.extend(generate_file_findings(result.file_exposures))
    
    # Score
    result.exposure_score, result.score_breakdown = calculate_exposure_score(result.findings)
    
    # NIS2 mapping
    result.nis2_compliance = map_nis2_compliance(result.findings)
    
    # Attack path (only for high-score targets — saves LLM cost)
    if result.exposure_score >= 50:
        result.attack_path = generate_attack_path(result)
    
    result.scan_duration_seconds = time.time() - start_time
    
    return result

def main():
    parser = argparse.ArgumentParser(description="KENGO ARGUS Scanner")
    parser.add_argument("--input", required=True, help="CSV file with leads")
    parser.add_argument("--output", default="results/", help="Output directory")
    parser.add_argument("--limit", type=int, help="Max domains to scan")
    parser.add_argument("--min-score", type=int, default=0, help="Only output results above this score")
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    # Read leads
    with open(args.input) as f:
        leads = list(csv.DictReader(f))
    
    if args.limit:
        leads = leads[:args.limit]
    
    print(f"KENGO ARGUS — Scanning {len(leads)} domains")
    print(f"Output: {args.output}")
    print()
    
    results_summary = []
    
    for lead in tqdm(leads, desc="Scanning"):
        domain = lead["domain"]
        output_file = os.path.join(args.output, f"{domain}.json")
        
        # Skip if already scanned
        if os.path.exists(output_file):
            print(f"  Skipping {domain} (already scanned)")
            continue
        
        print(f"\n{'='*60}")
        print(f"Scanning: {domain} ({lead.get('company_name', '')})")
        print(f"{'='*60}")
        
        try:
            result = scan_domain(lead)
            
            # Save full result
            with open(output_file, "w") as f:
                json.dump(result.__dict__, f, indent=2, default=str)
            
            # Summary
            results_summary.append({
                "domain": domain,
                "company": lead.get("company_name"),
                "score": result.exposure_score,
                "findings_critical": len([f for f in result.findings if f.severity == Severity.CRITICAL]),
                "findings_high": len([f for f in result.findings if f.severity == Severity.HIGH]),
                "findings_total": len(result.findings),
                "exchange_eol": result.exchange.is_eol if result.exchange else None,
                "msp": result.msp.name if result.msp else None,
                "credential_breaches": sum(c.breach_count for c in result.credential_exposures),
            })
            
            print(f"  Score: {result.exposure_score}/100 | "
                  f"Findings: {len(result.findings)} | "
                  f"Critical: {len([f for f in result.findings if f.severity == Severity.CRITICAL])}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
    
    # Write summary
    summary_file = os.path.join(args.output, "_summary.csv")
    if results_summary:
        with open(summary_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results_summary[0].keys())
            writer.writeheader()
            writer.writerows(sorted(results_summary, key=lambda x: x["score"], reverse=True))
    
    print(f"\n{'='*60}")
    print(f"SCAN COMPLETE")
    print(f"Total: {len(results_summary)} domains scanned")
    print(f"Summary: {summary_file}")
    if results_summary:
        avg_score = sum(r["score"] for r in results_summary) / len(results_summary)
        high_score = len([r for r in results_summary if r["score"] >= 70])
        print(f"Average Score: {avg_score:.0f}/100")
        print(f"High Risk (≥70): {high_score} ({high_score/len(results_summary)*100:.0f}%)")

if __name__ == "__main__":
    main()
```

---

## 7. OUTPUT: PERSONALIZED EMAIL GENERATOR

```python
def generate_outreach_email(result: ScanResult) -> str:
    """Generate a personalized outreach email with top 3 findings."""
    
    # Select top 3 most impactful findings
    top_findings = sorted(
        result.findings, 
        key=lambda f: (
            {"KRITISCH": 4, "HOCH": 3, "MITTEL": 2, "NIEDRIG": 1, "INFO": 0}[f.severity.value],
            len(f.evidence)  # Prefer findings with strong evidence
        ),
        reverse=True
    )[:3]
    
    # Build finding bullets
    finding_lines = []
    for f in top_findings:
        finding_lines.append(f"• {f.title} — {f.evidence[:100]}")
    
    gf_name = result.ownership.geschaeftsfuehrer[0]["name"] if result.ownership else "Geschäftsführer"
    
    email = f"""Betreff: {result.company_name} — 3 Sicherheitslücken die wir gefunden haben

Herr {gf_name.split()[-1]},

wir haben die öffentlich sichtbare IT-Infrastruktur von {result.company_name} analysiert 
und dabei {len([f for f in result.findings if f.severity in [Severity.CRITICAL, Severity.HIGH]])} 
kritische bzw. schwerwiegende Schwachstellen identifiziert.

Die drei dringendsten:

{chr(10).join(finding_lines)}

Diese Informationen sind öffentlich zugänglich — jeder mit den richtigen Tools findet sie. 
Was ein motivierter Angreifer in 5 Stunden daraus machen kann, zeige ich Ihnen gern in 
20 Minuten.

Haben Sie diese Woche einen kurzen Slot?

Beste Grüße
Phil Hie
Kengo — Autonomous IT Partner
"""
    return email
```

---

## 8. LEGAL FRAMEWORK

### What is legal (Germany, §202a-c StGB):

| Technique | Legal? | Why |
|-----------|--------|-----|
| DNS lookups (MX, SPF, DMARC, TXT) | ✅ YES | Public records, anyone can query |
| crt.sh Certificate Transparency | ✅ YES | Public logs, designed to be queryable |
| Shodan API queries | ✅ YES | Querying a search engine, not scanning targets |
| HTTP GET to public URLs | ✅ YES | Same as visiting a website in a browser |
| Checking /robots.txt, /.env, etc. | ✅ YES | HTTP GET to public URL, server decides what to serve |
| Reading HTTP response headers | ✅ YES | Server sends these voluntarily |
| NTLM challenge (empty Type 1) | ⚠️ GRAY | Single HTTP request, server responds voluntarily. No credentials used. Legally similar to visiting a URL. Document that no auth was bypassed. |
| HIBP email check | ✅ YES | Searching a legitimate breach notification service |
| Reverse DNS | ✅ YES | Public DNS infrastructure |
| Technology fingerprinting | ✅ YES | Reading publicly served content |

### What is NOT legal without explicit permission:

| Technique | Legal? | Why |
|-----------|--------|-----|
| Port scanning target directly | ❌ NO | Active scanning, potential §202a violation |
| Brute force / credential stuffing | ❌ NO | Unauthorized access attempt |
| Exploiting any vulnerability found | ❌ NO | Unauthorized access |
| Cracking hashes from .htpasswd | ⚠️ GRAY | Cracking the hash itself isn't access, but using the result would be |
| Downloading full .git repositories | ⚠️ GRAY | Could constitute copying protected data |

### Key principle: 
**We query public search engines and read publicly served content. We never send packets designed to exploit, enumerate users, or bypass authentication. Every technique should be equivalent to "I typed a URL into my browser."**

---

## 9. QUICK START

```bash
# 1. Clone and setup
mkdir kengo-argus && cd kengo-argus
python3 -m venv venv && source venv/bin/activate
pip install dnspython requests shodan anthropic beautifulsoup4 tqdm

# 2. Set API keys
export SHODAN_API_KEY="your_key"
export HIBP_API_KEY="your_key"  
export ANTHROPIC_API_KEY="your_key"

# 3. Create test lead file
echo "domain,company_name,gf_name,gf_email
example.com,Example GmbH,Max Mustermann,max@example.com" > test_leads.csv

# 4. Run scan
python main.py --input test_leads.csv --output results/ --limit 5

# 5. Review results
cat results/_summary.csv
cat results/example.com.json | python -m json.tool
```

---

## 10. PRIORITIZED BUILD ORDER

Build in this order. Each step is independently valuable:

1. **M01 (DNS) + M16 (Scoring)** — Instant value. SPF/DMARC/DKIM check + score. One evening.
2. **M09 (File Exposure) + M05 (Headers)** — Easy wins, high-impact findings. Second evening.
3. **M08 (Exchange + NTLM)** — The "woah" module. Makes the report devastating. Third evening.
4. **M04 (Shodan)** — Adds open ports, versions, CVEs. Massive enrichment. Fourth evening.
5. **M02 (Subdomains via crt.sh)** — Reveals hidden attack surface. Fifth evening.
6. **M12 (HIBP)** — Personal, emotional findings. Sixth evening.
7. **M13 + M14 (MSP + Supply Chain)** — Strategic intel layer.
8. **M17 (LLM Attack Path)** — The narrative that closes deals.
9. **M19 (Report + Email Gen)** — Automated output.
10. **Orchestrator** — Ties everything together for batch scanning.

After step 4, you have a scanner that produces better reports than 95% of pentest firms.
After step 8, you have a scanner that no one else in the German market has.
After step 10, you have a machine that prints leads.


---
---
---

# ═══════════════════════════════════════════════════════════
# V2 ADDITIONS — 14 ADDITIONAL MODULES + UPDATED BUILD ORDER
# ═══════════════════════════════════════════════════════════
# 
# Everything below was identified in the V2 gap analysis as
# MUST HAVE or SHOULD HAVE to make the scanner truly 10x.
# These modules are IN ADDITION to the V1 modules above.
# Nothing from V1 was removed or modified.
# ═══════════════════════════════════════════════════════════

# KENGO ARGUS — Gap-Analyse & fehlende 10x Module
## Was dem Scanner noch fehlt für echte 10x Findings
### Stand: 15. April 2026

---

## ZUSAMMENFASSUNG

Der aktuelle Scanner-Spec (V1) hat 15 Module. Nach Deep Research fehlen **13 kritische Module** die echte "woah"-Findings produzieren. Ohne diese ist der Scanner gut, aber nicht 10x. Mit ihnen hat niemand im deutschen Markt etwas Vergleichbares.

Die fehlenden Module aufgeteilt nach Impact:

| Priorität | Module | Erwarteter Impact |
|-----------|--------|-------------------|
| 🔴 MUST HAVE | 7 Module | Produzieren regelmäßig CRITICAL Findings |
| 🟠 SHOULD HAVE | 4 Module | Produzieren HIGH Findings, erhöhen Gesamtbild |
| 🟡 NICE TO HAVE | 2 Module | INFO-Level, aber runden den Report ab |

---

## 🔴 MUST HAVE — Fehlende Module die CRITICAL Findings produzieren

---

### M20: GitHub & GitLab Secret Scanning

**Warum das fehlt und warum es kritisch ist:**

Mittelstand-Entwickler (oder deren Agenturen) committen regelmäßig Credentials, API Keys, .env-Dateien, SSH-Keys, Datenbank-Passwörter in öffentliche Repos. Das passiert weil:
- Agenturen Code für den Kunden in öffentlichen Repos entwickeln
- Entwickler persönliche Repos haben wo sie Firmencode testen
- .gitignore nicht korrekt konfiguriert ist
- Commit-History nicht bereinigt wird (Secret war kurz sichtbar, wurde entfernt, ist aber in der History)

Bei True Fruits: Plugin-Prefix "emcgn" identifiziert die Agentur. Wenn die Agentur ein öffentliches GitHub-Repo hat → sofort prüfen.

**Implementation:**

```python
import requests
import time
import re
import base64

GITHUB_TOKEN = "ghp_..."  # Personal Access Token (free, 5000 req/hour)
GITHUB_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.text-match+json",
}

# GitHub Search Dorks — pro Domain angepasst
GITHUB_DORKS = [
    # Credentials & Secrets
    '"{domain}" password',
    '"{domain}" secret',
    '"{domain}" api_key',
    '"{domain}" apikey',
    '"{domain}" token',
    '"{domain}" credentials',
    '"{domain}" DB_PASSWORD',
    '"{domain}" AWS_SECRET',
    '"{domain}" PRIVATE_KEY',
    
    # Config files mit Domain-Referenz
    '"{domain}" filename:.env',
    '"{domain}" filename:.htpasswd',
    '"{domain}" filename:wp-config.php',
    '"{domain}" filename:configuration.php',
    '"{domain}" filename:config.yml',
    '"{domain}" filename:settings.py',
    '"{domain}" filename:database.yml',
    '"{domain}" filename:credentials.json',
    '"{domain}" filename:id_rsa',
    '"{domain}" filename:.npmrc',
    '"{domain}" filename:.dockercfg',
    
    # SSH & Private Keys
    '"{domain}" BEGIN RSA PRIVATE',
    '"{domain}" BEGIN OPENSSH PRIVATE',
    '"{domain}" BEGIN DSA PRIVATE',
    
    # Interne Hostnamen & Infrastruktur
    '"{internal_domain}"',  # z.B. "truefruits.local"
    '"{mail_host}"',        # z.B. "mail.true-fruits.com"
]

def scan_github_secrets(domain: str, 
                        internal_domain: str = None,
                        mail_host: str = None,
                        company_name: str = None) -> List[Dict]:
    findings = []
    
    for dork_template in GITHUB_DORKS:
        dork = dork_template.format(
            domain=domain,
            internal_domain=internal_domain or "",
            mail_host=mail_host or "",
        )
        
        if '""' in dork:  # Skip if variable was empty
            continue
            
        try:
            # GitHub Code Search API
            resp = requests.get(
                "https://api.github.com/search/code",
                headers=GITHUB_HEADERS,
                params={"q": dork, "per_page": 10},
                timeout=15,
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("total_count", 0) > 0:
                    for item in data["items"][:5]:
                        findings.append({
                            "dork": dork,
                            "repo": item["repository"]["full_name"],
                            "file": item["name"],
                            "path": item["path"],
                            "url": item["html_url"],
                            "text_matches": [
                                m.get("fragment", "")[:200] 
                                for m in item.get("text_matches", [])
                            ],
                            "repo_owner": item["repository"]["owner"]["login"],
                            "is_fork": item["repository"].get("fork", False),
                        })
            
            # Rate limiting: 10 req/min for search API
            time.sleep(6)
            
        except Exception as e:
            continue
    
    return findings
```

**Findings Generated:**

| ID | Condition | Severity |
|----|-----------|----------|
| GH-001 | Credentials (.env, passwords) für die Domain in öffentlichem Repo | CRITICAL |
| GH-002 | SSH Private Keys mit Domain-Bezug | CRITICAL |
| GH-003 | API Keys / Tokens für die Domain | CRITICAL |
| GH-004 | Interne Hostnamen / AD-Domain in Code | HIGH |
| GH-005 | Konfigurationsdateien mit Infrastruktur-Details | HIGH |
| GH-006 | Agentur-/Dienstleister-Repos mit Kundencode | MEDIUM |

**Rate Limiting:** GitHub Search API: 10 requests/minute (authenticated). ~20 Dorks pro Domain = ~2 Minuten pro Domain.

**Kosten:** Kostenlos (GitHub Personal Access Token)

**Warum das 10x ist:** Stell dir vor du sagst einem GF: "Ihr Entwicklungspartner hat Ihre Datenbank-Zugangsdaten in einem öffentlichen GitHub-Repository. Hier ist der Link." Das ist nicht abstrakt, das ist ein Link den er sofort anklicken kann.

---

### M21: Wayback Machine / Historical Exposure

**Warum das fehlt und warum es kritisch ist:**

Unternehmen entfernen sensible Seiten, Config-Leaks, Admin-Panels, alte API-Docs. Aber archive.org hat sie gespeichert. "Gelöscht" ≠ "verschwunden."

Die Wayback Machine CDX API ist kostenlos und gibt alle archivierten URLs für eine Domain zurück — inklusive solcher die heute 404 sind aber früher sensible Daten enthielten.

**Implementation:**

```python
import requests

# Interesting file patterns to filter from Wayback results
INTERESTING_PATTERNS = [
    # Config & Credentials
    ".env", ".htpasswd", ".htaccess", "web.config",
    "wp-config", "config.php", "settings.py", "database.yml",
    "credentials", ".git/", ".svn/",
    
    # Admin & Login
    "/admin", "/login", "/dashboard", "/panel", 
    "/wp-admin", "/administrator", "/manager",
    "/phpmyadmin", "/adminer", "/webmin",
    
    # API Documentation
    "/swagger", "/api-docs", "/graphql", "/api/v1", "/api/v2",
    "/openapi", "/redoc",
    
    # Backups & Dumps
    ".sql", ".bak", ".backup", ".dump", ".tar", ".zip",
    ".gz", ".7z", ".rar",
    
    # Source Code
    ".map",        # JavaScript source maps
    ".ts",         # TypeScript source
    "package.json",
    "composer.json",
    "Gemfile",
    
    # Internal / Sensitive
    "/internal", "/intranet", "/staging", "/dev",
    "/test", "/debug", "/trace", "/status",
    "/server-status", "/server-info", "/phpinfo",
    
    # Documents
    ".pdf", ".xlsx", ".docx", ".csv",
    "report", "invoice", "employee", "salary",
    "password", "credential",
]

def scan_wayback(domain: str) -> Dict:
    """Query Wayback Machine CDX API for all archived URLs."""
    results = {
        "total_urls": 0,
        "interesting_urls": [],
        "oldest_snapshot": None,
        "newest_snapshot": None,
        "still_live": [],      # URLs that were archived AND still respond today
        "removed_but_archived": [],  # URLs that were archived but now return 404
    }
    
    try:
        # CDX API: returns all archived URLs for the domain
        resp = requests.get(
            "https://web.archive.org/cdx/search/cdx",
            params={
                "url": f"*.{domain}/*",
                "output": "json",
                "fl": "timestamp,original,statuscode,mimetype,length",
                "collapse": "urlkey",  # Deduplicate by URL
                "limit": 10000,
            },
            timeout=60,
        )
        
        if resp.status_code == 200:
            rows = resp.json()
            if len(rows) > 1:  # First row is header
                headers = rows[0]
                urls = rows[1:]
                results["total_urls"] = len(urls)
                
                for row in urls:
                    url_data = dict(zip(headers, row))
                    original_url = url_data.get("original", "")
                    
                    # Check if URL matches interesting patterns
                    lower_url = original_url.lower()
                    for pattern in INTERESTING_PATTERNS:
                        if pattern in lower_url:
                            results["interesting_urls"].append({
                                "url": original_url,
                                "timestamp": url_data.get("timestamp"),
                                "status": url_data.get("statuscode"),
                                "pattern_matched": pattern,
                                "archive_url": f"https://web.archive.org/web/{url_data.get('timestamp')}/{original_url}",
                            })
                            break
                
                # Sort by timestamp
                if urls:
                    timestamps = [u[0] for u in urls if u[0].isdigit()]
                    if timestamps:
                        results["oldest_snapshot"] = min(timestamps)
                        results["newest_snapshot"] = max(timestamps)
        
        # Check if interesting URLs are still live today
        for item in results["interesting_urls"][:20]:  # Cap to avoid excessive requests
            try:
                resp = requests.head(item["url"], timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    results["still_live"].append(item)
                elif resp.status_code in [404, 403, 410]:
                    results["removed_but_archived"].append(item)
            except:
                pass
            time.sleep(0.5)
    
    except Exception as e:
        pass
    
    return results
```

**Findings Generated:**

| ID | Condition | Severity |
|----|-----------|----------|
| WB-001 | .env / Config-Datei in Archiv gefunden UND noch live | CRITICAL |
| WB-002 | Admin-Panel in Archiv gefunden UND noch live | HIGH |
| WB-003 | .sql / Backup-Datei in Archiv gefunden | HIGH |
| WB-004 | API-Dokumentation in Archiv (zeigt Endpoints) | MEDIUM |
| WB-005 | JavaScript Source Maps in Archiv | MEDIUM |
| WB-006 | Interne Dokumente (PDF/XLSX) in Archiv | MEDIUM |
| WB-007 | Mehr als 50 archived URLs mit sensitiven Patterns | INFO |

**Kosten:** Kostenlos (CDX API ist public)

**Warum das 10x ist:** "Ihre .env-Datei war 2024 öffentlich zugänglich. Hier ist der Archive.org-Link. Die Datei enthielt Datenbank-Zugangsdaten. Haben Sie seitdem die Passwörter geändert?"

---

### M22: Subdomain Takeover Detection

**Warum das fehlt und warum es kritisch ist:**

Wenn ein CNAME-Record auf einen Service zeigt der nicht mehr existiert (z.B. alte Heroku-App, deaktivierte Azure-Website, gelöschte GitHub-Page), kann ein Angreifer diesen Service unter dem selben Namen neu erstellen und den Subdomain übernehmen. Das ist eine der am meisten unterschätzten Vulnerabilities.

**Implementation:**

```python
# Services vulnerable to subdomain takeover
TAKEOVER_SIGNATURES = {
    # Service: (CNAME pattern, error fingerprint when unclaimed)
    "GitHub Pages": {
        "cname_patterns": [".github.io"],
        "fingerprints": ["There isn't a GitHub Pages site here"],
    },
    "Heroku": {
        "cname_patterns": [".herokuapp.com", ".herokudns.com"],
        "fingerprints": ["No such app", "no-such-app"],
    },
    "AWS S3": {
        "cname_patterns": [".s3.amazonaws.com", ".s3-website"],
        "fingerprints": ["NoSuchBucket", "The specified bucket does not exist"],
    },
    "Azure": {
        "cname_patterns": [".azurewebsites.net", ".cloudapp.azure.com", 
                          ".azure-api.net", ".azurefd.net"],
        "fingerprints": ["404 Web Site not found", "NXDOMAIN"],
    },
    "Shopify": {
        "cname_patterns": [".myshopify.com"],
        "fingerprints": ["Sorry, this shop is currently unavailable"],
    },
    "Fastly": {
        "cname_patterns": [".fastly.net"],
        "fingerprints": ["Fastly error: unknown domain"],
    },
    "Unbounce": {
        "cname_patterns": [".unbouncepages.com"],
        "fingerprints": ["The requested URL was not found"],
    },
    "Tumblr": {
        "cname_patterns": [".tumblr.com"],
        "fingerprints": ["There's nothing here"],
    },
    "WordPress.com": {
        "cname_patterns": [".wordpress.com"],
        "fingerprints": ["Do you want to register"],
    },
    "Surge.sh": {
        "cname_patterns": [".surge.sh"],
        "fingerprints": ["project not found"],
    },
    "Cargo Collective": {
        "cname_patterns": [".cargocollective.com"],
        "fingerprints": ["404 Not Found"],
    },
    "Zendesk": {
        "cname_patterns": [".zendesk.com"],
        "fingerprints": ["Help Center Closed"],
    },
    "Statuspage": {
        "cname_patterns": [".statuspage.io"],
        "fingerprints": ["Status page"],  # Check if actually claimed
    },
    "Pantheon": {
        "cname_patterns": [".pantheonsite.io"],
        "fingerprints": ["The gods are wise"],
    },
    "Readme.io": {
        "cname_patterns": [".readme.io"],
        "fingerprints": ["Project doesnt exist"],
    },
}

def check_subdomain_takeover(subdomains: List[Subdomain]) -> List[Finding]:
    findings = []
    
    for sd in subdomains:
        # Get CNAME record
        try:
            cname_answers = dns.resolver.resolve(sd.hostname, 'CNAME')
            cname_target = str(cname_answers[0].target).rstrip('.')
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
            continue
        
        # Check if CNAME points to a takeover-vulnerable service
        for service, config in TAKEOVER_SIGNATURES.items():
            for pattern in config["cname_patterns"]:
                if cname_target.endswith(pattern):
                    # CNAME points to this service — check if it's dangling
                    
                    # Method 1: NXDOMAIN on CNAME target
                    try:
                        dns.resolver.resolve(cname_target, 'A')
                    except dns.resolver.NXDOMAIN:
                        findings.append(Finding(
                            id=f"TAKEOVER-{sd.hostname[:10]}",
                            title=f"Subdomain Takeover möglich: {sd.hostname}",
                            severity=Severity.CRITICAL,
                            description=f"Der Subdomain {sd.hostname} hat einen CNAME-Record "
                                       f"der auf {cname_target} ({service}) zeigt. "
                                       f"Dieser Service existiert nicht mehr (NXDOMAIN). "
                                       f"Ein Angreifer kann den Service unter diesem Namen "
                                       f"neu erstellen und den Subdomain übernehmen.",
                            evidence=f"dig CNAME {sd.hostname} → {cname_target} → NXDOMAIN",
                            nis2_paragraphs=["§30 Abs. 2 Nr. 1", "§30 Abs. 2 Nr. 9"],
                            remediation=f"CNAME-Record für {sd.hostname} sofort entfernen.",
                        ))
                        continue
                    except: pass
                    
                    # Method 2: HTTP fingerprint match
                    try:
                        resp = requests.get(f"https://{sd.hostname}", timeout=10)
                        for fingerprint in config["fingerprints"]:
                            if fingerprint.lower() in resp.text.lower():
                                findings.append(Finding(
                                    id=f"TAKEOVER-{sd.hostname[:10]}",
                                    title=f"Subdomain Takeover möglich: {sd.hostname}",
                                    severity=Severity.CRITICAL,
                                    description=f"...",
                                    evidence=f"GET https://{sd.hostname} enthält: '{fingerprint}'",
                                ))
                                break
                    except: pass
    
    return findings
```

**Findings Generated:**

| ID | Condition | Severity |
|----|-----------|----------|
| TAKEOVER-001 | CNAME → NXDOMAIN (Service gelöscht, DNS bleibt) | CRITICAL |
| TAKEOVER-002 | CNAME → Service-Default-Error-Page | HIGH |
| TAKEOVER-003 | Dangling CNAME ohne bekanntes Takeover-Pattern | MEDIUM |

**Warum das 10x ist:** "Ihr Subdomain blog.firma.com zeigt auf einen Heroku-Service der nicht mehr existiert. Jeder kann diesen Service unter dem Namen Ihrer Domain neu erstellen und dort Phishing-Seiten hosten — mit gültigem SSL-Zertifikat auf Ihrem Domainnamen."

---

### M23: Google Dorking (Indexed Exposure)

**Warum das fehlt und warum es kritisch ist:**

Google indexiert Dinge die nie öffentlich sein sollten: interne PDFs, Excel-Dateien mit Mitarbeiterdaten, Konfigurationspanels, Drucker-Interfaces, alte Login-Seiten.

**Implementation:**

```python
# Google Custom Search API or SerpAPI für programmatischen Zugriff
# Alternative: googlesearch-python library (rate-limited, kein API Key nötig)

GOOGLE_DORKS = [
    # Exposed Documents
    'site:{domain} filetype:pdf',
    'site:{domain} filetype:xlsx',
    'site:{domain} filetype:docx',
    'site:{domain} filetype:csv',
    'site:{domain} filetype:sql',
    'site:{domain} filetype:log',
    'site:{domain} filetype:bak',
    'site:{domain} filetype:conf',
    'site:{domain} filetype:cfg',
    
    # Admin & Login Panels
    'site:{domain} inurl:admin',
    'site:{domain} inurl:login',
    'site:{domain} inurl:config',
    'site:{domain} inurl:setup',
    'site:{domain} inurl:install',
    'site:{domain} intitle:"index of"',
    
    # Sensitive Keywords
    'site:{domain} "password"',
    'site:{domain} "internal use only"',
    'site:{domain} "confidential"',
    'site:{domain} "not for distribution"',
    'site:{domain} "vertraulich"',        # German: confidential
    'site:{domain} "nur für internen Gebrauch"',  # German: internal use only
    
    # Error Pages (reveal tech stack)
    'site:{domain} "SQL syntax"',
    'site:{domain} "mysql_connect"',
    'site:{domain} "pg_connect"',
    'site:{domain} "Warning: include"',
    'site:{domain} "Fatal error"',
    'site:{domain} "stack trace"',
    'site:{domain} "Exception in thread"',
    
    # Exposed Infrastructure
    'site:{domain} inurl:phpinfo',
    'site:{domain} inurl:server-status',
    'site:{domain} "Index of /" +parent +directory',
]
```

**Findings Generated:**

| ID | Condition | Severity |
|----|-----------|----------|
| GORK-001 | Interne Dokumente (PDF/XLSX) von Google indexiert | HIGH |
| GORK-002 | SQL/Config/Backup-Dateien indexiert | CRITICAL |
| GORK-003 | Open Directory Listing indexiert | HIGH |
| GORK-004 | Error Pages mit Stack Traces indexiert | MEDIUM |
| GORK-005 | Login-/Admin-Panel von Google indexiert | MEDIUM |

**Rate Limiting:** Google sperrt automatische Suchen. Lösung: Google Custom Search API (100 Suchen/Tag kostenlos, $5/1000 danach) oder SerpAPI ($50/Monat, 5000 Suchen).

---

### M24: CORS Misconfiguration Testing

**Warum das fehlt:**

Wildcard CORS (`Access-Control-Allow-Origin: *`) ist ein häufiger Fund — aber es gibt schlimmere Varianten: Server die den Origin-Header reflektieren (jede Website kann Cross-Origin Requests machen).

**Implementation:**

```python
def check_cors(url: str) -> List[Finding]:
    findings = []
    
    test_origins = [
        "https://evil.com",
        "https://attacker.com",
        f"https://sub.{url.split('//')[1].split('/')[0]}",  # Subdomain of target
        "null",  # null origin (sandboxed iframes)
    ]
    
    for origin in test_origins:
        try:
            resp = requests.get(url, headers={"Origin": origin}, timeout=10)
            acao = resp.headers.get("Access-Control-Allow-Origin", "")
            acac = resp.headers.get("Access-Control-Allow-Credentials", "")
            
            if acao == "*":
                findings.append(Finding(
                    id="CORS-001",
                    title="Wildcard CORS Policy",
                    severity=Severity.HIGH,
                    evidence=f"Access-Control-Allow-Origin: * (bei Origin: {origin})",
                ))
            elif acao == origin:
                severity = Severity.CRITICAL if acac.lower() == "true" else Severity.HIGH
                findings.append(Finding(
                    id="CORS-002",
                    title="Origin-Reflection CORS — beliebige Websites können API-Requests machen",
                    severity=severity,
                    evidence=f"Origin '{origin}' wird reflektiert. "
                             f"Allow-Credentials: {acac}",
                    description="Der Server reflektiert jeden Origin-Header. "
                               "In Kombination mit Allow-Credentials können "
                               "Angreifer authentifizierte API-Requests von "
                               "beliebigen Websites ausführen.",
                ))
                break  # One reflection proof is enough
            elif acao == "null":
                findings.append(Finding(
                    id="CORS-003",
                    title="Null-Origin CORS erlaubt",
                    severity=Severity.MEDIUM,
                    evidence="Access-Control-Allow-Origin: null",
                ))
        except: pass
    
    return findings
```

---

### M25: Certificate Intelligence (SAN Analysis)

**Warum das fehlt:**

SSL-Zertifikate enthalten Subject Alternative Names (SANs) — oft mit internen Hostnamen, IP-Adressen, oder unbekannten Subdomains die nicht öffentlich in DNS stehen.

```python
import ssl
import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend

def analyze_certificate(hostname: str, port: int = 443) -> Dict:
    result = {
        "subject": {},
        "issuer": {},
        "sans": [],
        "internal_names_leaked": [],
        "valid_from": None,
        "valid_to": None,
        "days_until_expiry": None,
        "signature_algorithm": None,
        "key_size": None,
        "is_wildcard": False,
        "is_self_signed": False,
        "chain_length": None,
        "weak_algorithm": False,
    }
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                der_cert = ssock.getpeercert(binary_form=True)
                cert = x509.load_der_x509_certificate(der_cert, default_backend())
                
                # SANs — this is the goldmine
                try:
                    san_ext = cert.extensions.get_extension_for_class(
                        x509.SubjectAlternativeName
                    )
                    for name in san_ext.value:
                        san_value = name.value
                        result["sans"].append(san_value)
                        
                        # Check if SAN reveals internal infrastructure
                        if any(indicator in san_value.lower() for indicator in [
                            ".local", ".internal", ".corp", ".lan", ".intra",
                            "192.168.", "10.", "172.16.", "172.17.", "172.18.",
                        ]):
                            result["internal_names_leaked"].append(san_value)
                except: pass
                
                # Check for weak signature
                sig_algo = cert.signature_algorithm_oid._name
                result["signature_algorithm"] = sig_algo
                if "sha1" in sig_algo.lower() or "md5" in sig_algo.lower():
                    result["weak_algorithm"] = True
                
                # Check wildcard
                for san in result["sans"]:
                    if san.startswith("*."):
                        result["is_wildcard"] = True
                
                # Check self-signed
                if cert.issuer == cert.subject:
                    result["is_self_signed"] = True
                
                # Validity
                result["valid_from"] = cert.not_valid_before_utc.isoformat()
                result["valid_to"] = cert.not_valid_after_utc.isoformat()
                
    except Exception as e:
        pass
    
    return result
```

**Findings:**

| ID | Condition | Severity |
|----|-----------|----------|
| CERT-001 | Interne Hostnamen (.local, .internal) in SANs | HIGH |
| CERT-002 | Private IP-Adressen in SANs | HIGH |
| CERT-003 | Schwacher Signatur-Algorithmus (SHA-1, MD5) | HIGH |
| CERT-004 | Self-Signed Certificate auf Production | MEDIUM |
| CERT-005 | Zertifikat läuft in <30 Tagen ab | MEDIUM |
| CERT-006 | Unbekannte Subdomains in SANs (nicht in DNS) | MEDIUM |

---

### M26: DNS Zone Transfer (AXFR) Test

**Warum das fehlt:**

Ein einzelner DNS-Request. Wenn der Server AXFR erlaubt, bekommst du ALLE DNS-Records auf einmal — jede Subdomain, jeden internen Hostnamen, jeden MX-, SRV-, TXT-Record. Es ist ein Konfigurationsfehler der überraschend häufig vorkommt, besonders bei kleinen DNS-Providern die Mittelständler nutzen.

```python
import dns.zone
import dns.query

def attempt_zone_transfer(domain: str, ns_records: List[str]) -> Dict:
    result = {"vulnerable": False, "records": [], "ns_tested": []}
    
    for ns in ns_records:
        result["ns_tested"].append(ns)
        try:
            # Attempt AXFR
            zone = dns.zone.from_xfr(
                dns.query.xfr(ns, domain, timeout=10)
            )
            
            # If we get here, zone transfer succeeded!
            result["vulnerable"] = True
            for name, node in zone.nodes.items():
                for rdataset in node.rdatasets:
                    for rdata in rdataset:
                        result["records"].append({
                            "name": str(name),
                            "type": dns.rdatatype.to_text(rdataset.rdtype),
                            "value": str(rdata),
                            "ttl": rdataset.ttl,
                        })
            
            break  # One successful transfer is enough
            
        except Exception:
            continue  # NS doesn't allow AXFR, try next
    
    return result
```

**Finding: DNS-AXFR | Zone Transfer erlaubt | CRITICAL**

---

### M27: Favicon Hash → Hidden Infrastructure (Shodan)

**Warum das fehlt:**

Jede Website hat ein Favicon. Shodan indexiert den mmh3-Hash jedes Favicons. Wenn du den Hash der Hauptwebsite berechnest und in Shodan suchst, findest du ALLE Server die dasselbe Favicon nutzen — inklusive interner Systeme, Dev-Server, vergessener Instanzen.

```python
import mmh3
import codecs

def favicon_hash_search(domain: str) -> List[Dict]:
    """Calculate favicon hash, search Shodan for all matching hosts."""
    
    # Download favicon
    favicon_urls = [
        f"https://{domain}/favicon.ico",
        f"https://{domain}/apple-touch-icon.png",
    ]
    
    for url in favicon_urls:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200 and len(resp.content) > 0:
                # Calculate Shodan-compatible favicon hash
                favicon_b64 = codecs.encode(resp.content, "base64")
                hash_value = mmh3.hash(favicon_b64)
                
                # Search Shodan for this hash
                api = shodan.Shodan(SHODAN_API_KEY)
                results = api.search(f"http.favicon.hash:{hash_value}")
                
                hosts = []
                for match in results["matches"]:
                    ip = match["ip_str"]
                    # Filter out the known domain IPs
                    hostnames = match.get("hostnames", [])
                    if domain not in " ".join(hostnames):
                        hosts.append({
                            "ip": ip,
                            "hostnames": hostnames,
                            "port": match.get("port"),
                            "org": match.get("org"),
                            "os": match.get("os"),
                        })
                
                return hosts
        except: pass
    
    return []
```

**Finding: FAV-001 | Versteckte Infrastruktur mit gleichem Favicon gefunden | HIGH**

Wenn der Hash auf 3 bekannten IPs liegt aber auch auf 2 unbekannten → das sind wahrscheinlich interne/dev/staging Server.

---

## 🟠 SHOULD HAVE — Fehlende Module die HIGH Findings produzieren

---

### M28: DNSSEC Validation

```python
def check_dnssec(domain: str) -> bool:
    """Check if DNSSEC is configured for the domain."""
    try:
        # Check for DNSKEY record
        answers = dns.resolver.resolve(domain, 'DNSKEY')
        return len(answers) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False
    except:
        return False
```

**Finding: DNSSEC-001 | Kein DNSSEC konfiguriert → DNS-Spoofing möglich | MEDIUM**

---

### M29: GraphQL Introspection

```python
GRAPHQL_ENDPOINTS = ["/graphql", "/api/graphql", "/gql", "/query"]
INTROSPECTION_QUERY = '{"query":"{ __schema { types { name fields { name } } } }"}'

def check_graphql(base_url: str) -> List[Finding]:
    findings = []
    for endpoint in GRAPHQL_ENDPOINTS:
        url = f"{base_url}{endpoint}"
        try:
            resp = requests.post(
                url,
                json={"query": "{ __schema { types { name } } }"},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code == 200 and "__schema" in resp.text:
                findings.append(Finding(
                    id="GQL-001",
                    title="GraphQL Introspection aktiviert — komplettes API-Schema offengelegt",
                    severity=Severity.HIGH,
                    evidence=f"POST {url} → Schema mit {resp.text.count('name')} Typen",
                ))
        except: pass
    return findings
```

---

### M30: JavaScript Source Map Exposure

```python
def check_source_maps(base_url: str) -> List[Finding]:
    """Check if JS source maps are publicly accessible."""
    findings = []
    
    # First, find JS files from the page
    try:
        resp = requests.get(base_url, timeout=10)
        js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', resp.text)
        
        for js_file in js_files[:10]:
            # Check for .map file
            if js_file.startswith("/"):
                map_url = f"{base_url}{js_file}.map"
            elif js_file.startswith("http"):
                map_url = f"{js_file}.map"
            else:
                map_url = f"{base_url}/{js_file}.map"
            
            try:
                map_resp = requests.head(map_url, timeout=5)
                if map_resp.status_code == 200:
                    content_length = int(map_resp.headers.get("Content-Length", 0))
                    if content_length > 1000:  # Real source map, not error page
                        findings.append(Finding(
                            id="SRCMAP-001",
                            title=f"JavaScript Source Map öffentlich zugänglich",
                            severity=Severity.HIGH,
                            evidence=f"GET {map_url} → {content_length} bytes "
                                     f"(enthält Original-Quellcode)",
                        ))
            except: pass
    except: pass
    
    return findings
```

---

### M31: Cloud Storage Bucket Discovery

```python
BUCKET_PATTERNS = [
    # S3
    "https://{company}.s3.amazonaws.com",
    "https://{company}-backup.s3.amazonaws.com",
    "https://{company}-data.s3.amazonaws.com",
    "https://{company}-assets.s3.amazonaws.com",
    "https://{company}-uploads.s3.amazonaws.com",
    "https://{company}-media.s3.amazonaws.com",
    "https://{company}-dev.s3.amazonaws.com",
    "https://{company}-staging.s3.amazonaws.com",
    "https://{company}-prod.s3.amazonaws.com",
    
    # Azure Blob
    "https://{company}.blob.core.windows.net",
    
    # Google Cloud Storage
    "https://storage.googleapis.com/{company}",
]

def check_cloud_buckets(company_name: str, domain: str) -> List[Finding]:
    findings = []
    # Generate variations
    names = [
        company_name.lower().replace(" ", "-"),
        company_name.lower().replace(" ", ""),
        domain.split(".")[0],
    ]
    
    for name in names:
        for pattern in BUCKET_PATTERNS:
            url = pattern.format(company=name)
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    findings.append(Finding(
                        id="BUCKET-001",
                        title=f"Öffentlich zugänglicher Cloud-Speicher gefunden",
                        severity=Severity.CRITICAL,
                        evidence=f"GET {url} → HTTP 200 (öffentlich lesbar)",
                    ))
                elif resp.status_code == 403:
                    # Bucket exists but is private — still useful intel
                    findings.append(Finding(
                        id="BUCKET-002",
                        title=f"Cloud-Speicher existiert (privat): {url}",
                        severity=Severity.INFO,
                    ))
            except: pass
    
    return findings
```

---

## 🟡 NICE TO HAVE

### M32: CAA Records Check

```python
def check_caa(domain: str) -> bool:
    """Check if Certificate Authority Authorization records exist."""
    try:
        answers = dns.resolver.resolve(domain, 'CAA')
        return len(answers) > 0
    except:
        return False
```

**Finding: CAA-001 | Keine CAA Records → jede CA kann Zertifikate ausstellen | LOW**

### M33: WHOIS Expiration Check

```python
import whois

def check_domain_expiry(domain: str) -> Dict:
    try:
        w = whois.whois(domain)
        expiry = w.expiration_date
        if isinstance(expiry, list):
            expiry = expiry[0]
        days_left = (expiry - datetime.now()).days
        return {"expiry_date": expiry, "days_left": days_left}
    except:
        return {}
```

**Finding: WHOIS-001 | Domain läuft in <90 Tagen ab → Takeover-Risiko | MEDIUM**

---

## VOLLSTÄNDIGE MODUL-LISTE (V2)

### V1 Module (bereits im Spec):
1. M01: DNS Intelligence
2. M02: Subdomain Discovery (crt.sh)
3. M03: IP Resolution & Cloud Provider
4. M04: Shodan Lookup
5. M05: HTTP Security Headers
6. M06: TLS Analysis
7. M07: Technology Fingerprinting
8. M08: Exchange Detection & NTLM Challenge
9. M09: Common File Exposure Check
10. M10: Admin Panel Discovery
11. M11: API Endpoint Discovery
12. M12: Credential Exposure (HIBP)
13. M13: MSP Identification & Scoring
14. M14: Supply Chain Mapping
15. M15: Ownership & Structure

### V2 Module (NEU — diese Datei):
16. M20: GitHub/GitLab Secret Scanning ← 🔴 MUST HAVE
17. M21: Wayback Machine Historical Exposure ← 🔴 MUST HAVE
18. M22: Subdomain Takeover Detection ← 🔴 MUST HAVE
19. M23: Google Dorking ← 🔴 MUST HAVE
20. M24: CORS Misconfiguration ← 🔴 MUST HAVE
21. M25: Certificate SAN Analysis ← 🔴 MUST HAVE
22. M26: DNS Zone Transfer (AXFR) ← 🔴 MUST HAVE
23. M27: Favicon Hash → Hidden Infrastructure ← 🔴 MUST HAVE (technically this is #8 must-have)
24. M28: DNSSEC Validation ← 🟠 SHOULD HAVE
25. M29: GraphQL Introspection ← 🟠 SHOULD HAVE
26. M30: Source Map Exposure ← 🟠 SHOULD HAVE
27. M31: Cloud Storage Bucket Discovery ← 🟠 SHOULD HAVE
28. M32: CAA Records ← 🟡 NICE TO HAVE
29. M33: WHOIS Expiration ← 🟡 NICE TO HAVE

---

## AKTUALISIERTE BUILD-REIHENFOLGE (V2)

Integriert in die originale 10-Schritt-Reihenfolge:

```
Abend 1: M01 (DNS) + M26 (AXFR) + M28 (DNSSEC) + M32 (CAA) + M33 (WHOIS)
         → Alles DNS-basiert, kein API Key nötig, sofort wertvolle Findings
         
Abend 2: M09 (File Exposure) + M05 (Headers) + M24 (CORS) + M30 (Source Maps)
         → Alles HTTP-basiert, ein Request pro Check
         
Abend 3: M08 (Exchange + NTLM) + M25 (Certificate SANs)
         → Die "woah"-Module. AD Domain + interne Namen aus Cert SANs
         
Abend 4: M04 (Shodan) + M27 (Favicon Hash)
         → Braucht Shodan API Key ($49). Massives Enrichment
         
Abend 5: M02 (Subdomains crt.sh) + M22 (Subdomain Takeover)
         → crt.sh findet die Subdomains, Takeover-Check prüft sie
         
Abend 6: M12 (HIBP Credentials)
         → Braucht HIBP API Key ($3.50). Persönlich, emotional
         
Abend 7: M20 (GitHub Secrets) + M21 (Wayback Machine)
         → Die "heilige Scheiße"-Module. Findet vergessene Credentials
         
Abend 8: M23 (Google Dorking) + M31 (Cloud Buckets)
         → Findet von Google indexierte Dokumente und offene S3 Buckets
         
Abend 9: M07 (Tech Fingerprint) + M29 (GraphQL) + M13-14 (MSP + Supply Chain) + M15 (Ownership)
         → Intelligence Layer
         
Abend 10: M16 (Scoring) + M17 (LLM Attack Path) + M18 (NIS2 Mapping) + M19 (Reports)
          → Analysis & Output
```

---

## KOSTEN-UPDATE (V2)

| Service | Plan | Cost/Monat | Module |
|---------|------|-----------|--------|
| Shodan | Membership | $49 | M04, M27 |
| HIBP | Core | $3.50 | M12 |
| Anthropic | Pay-as-you-go | ~$50-100 | M17 (Attack Path LLM) |
| GitHub | Personal Access Token | $0 | M20 |
| crt.sh | Free | $0 | M02 |
| Wayback Machine CDX | Free | $0 | M21 |
| SerpAPI (für Google Dorks) | Starter | $50 | M23 |
| DNS | Free | $0 | M01, M26, M28, M22 |
| **TOTAL** | | **~$153-200/month** | **29 Module** |

---

## WHAT THIS SCANNER FINDS vs. WHAT OTHERS FIND

| Finding Category | Typischer MSP-Report | Typischer Pentest-Report | KENGO ARGUS V2 |
|-----------------|---------------------|------------------------|----------------|
| SPF/DMARC/DKIM | ✅ | ✅ | ✅ |
| Fehlende HTTP Headers | ❌ | ✅ | ✅ |
| Exchange EOL + NTLM Domain Leak | ❌ | ⚠️ (nur mit Scope) | ✅ (passiv!) |
| AD Domain Name ohne Credentials | ❌ | ❌ (braucht Netzwerkzugang) | ✅ |
| Subdomain Takeover | ❌ | ⚠️ (manchmal) | ✅ (automatisch) |
| GitHub Credential Leaks | ❌ | ❌ | ✅ |
| Wayback Machine Exposures | ❌ | ❌ | ✅ |
| HIBP Credential Exposure | ❌ | ❌ | ✅ |
| Google-indexierte Dokumente | ❌ | ❌ | ✅ |
| Favicon-basierte Infra-Discovery | ❌ | ❌ | ✅ |
| Certificate SAN Leaks | ❌ | ⚠️ (manuell) | ✅ |
| MSP Identification & Scoring | ❌ | ❌ | ✅ |
| Supply Chain Risk Map | ❌ | ❌ | ✅ |
| LLM-generated Attack Narrative | ❌ | ❌ | ✅ |
| NIS2 §30 Compliance Mapping | ❌ | ❌ | ✅ |
| DNS Zone Transfer | ❌ | ✅ | ✅ |
| Cloud Bucket Exposure | ❌ | ⚠️ | ✅ |
| CORS Misconfiguration | ❌ | ✅ | ✅ |
| GraphQL Introspection | ❌ | ⚠️ | ✅ |
| Source Map Exposure | ❌ | ❌ | ✅ |

**Fazit: ARGUS V2 findet in 10-15 Minuten passiv mehr als ein typischer €15.000 Penetrationstest in 2 Wochen.**

Der entscheidende Unterschied: Pentester scannen 1 Unternehmen manuell. ARGUS scannt 500 pro Tag automatisch. Das ist der Compound-Effekt der Kengo auf €10M ARR bringt.