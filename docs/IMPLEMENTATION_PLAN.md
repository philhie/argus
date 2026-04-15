KENGO ARGUS — Implementation Plan

Context

Kengo is an AI-native managed IT/cybersecurity company targeting German Mittelstand (50-200 employees). ARGUS is the automated passive reconnaissance engine that scans company domains from the outside — legally, without permission — to find specific, verifiable vulnerabilities that drive outbound sales. The goal: produce findings so personal and devastating that CEOs pick up the phone. This scanner is the revenue engine behind Kengo’s path to €10M ARR.

The workspace is empty. We’re building from scratch based on the KENGO_ARGUS_FINAL_SPEC-v1.md (29 modules, 100+ finding types, ~€153-200/month all-in).

Project Structure

semarang/
├── argus/
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   ├── cli.py                   # argparse setup
│   ├── config.py                # Settings via pydantic-settings + .env
│   ├── models.py                # Finding, ScanContext, ScanResult, all data models
│   ├── scanner.py               # Orchestrator — runs modules in phase order
│   ├── scoring.py               # Exposure score calculation
│   ├── modules/
│   │   ├── __init__.py          # Module registry + auto-discovery
│   │   ├── base.py              # BaseModule ABC
│   │   ├── dns_intel.py         # M01: SPF/DMARC/DKIM/MTA-STS/DANE/BIMI/NS/TXT
│   │   ├── zone_transfer.py     # M26: AXFR test
│   │   ├── dnssec.py            # M28: DNSSEC validation
│   │   ├── caa.py               # M32: CAA records
│   │   ├── whois_check.py       # M33: Domain expiration
│   │   ├── file_exposure.py     # M09: 40+ sensitive file paths
│   │   ├── http_headers.py      # M05: Security headers + leaky headers
│   │   ├── cors.py              # M24: CORS misconfiguration
│   │   ├── source_maps.py       # M30: JS source map exposure
│   │   ├── exchange.py          # M08: Exchange detection + NTLM challenge
│   │   ├── cert_san.py          # M25: Certificate SAN analysis
│   │   ├── shodan_lookup.py     # M04: Ports/versions/CVEs
│   │   ├── favicon_hash.py      # M27: Favicon hash → Shodan
│   │   ├── subdomains.py        # M02: crt.sh + DNS brute
│   │   ├── subdomain_takeover.py# M31: Dangling CNAME detection
│   │   ├── hibp.py              # M12: Credential exposure
│   │   ├── github_secrets.py    # M29: GitHub/GitLab secret scanning
│   │   ├── wayback.py           # M30: Wayback Machine historical exposure
│   │   ├── google_dorks.py      # M23: Google dorking via SerpAPI
│   │   ├── cloud_buckets.py     # M33: S3/Azure/GCS bucket discovery
│   │   ├── tech_fingerprint.py  # M07: Technology detection
│   │   ├── graphql.py           # M29: GraphQL introspection
│   │   ├── msp.py               # M13: MSP identification & scoring
│   │   ├── supply_chain.py      # M14: Third-party mapping
│   │   ├── ownership.py         # M15: Company structure
│   │   ├── attack_path.py       # M17: LLM-generated kill chain
│   │   ├── nis2_mapping.py      # M18: NIS2 §30 compliance
│   │   └── report_gen.py        # M19: HTML report + email generation
│   └── data/
│       ├── exchange_versions.json
│       ├── takeover_signatures.json
│       ├── cloud_ip_ranges.json
│       ├── dkim_selectors.json
│       └── file_checks.json
├── tests/
│   ├── __init__.py
│   ├── test_dns_intel.py
│   ├── test_scoring.py
│   └── test_models.py
├── results/                     # Scan output (gitignored)
├── .env.example                 # Template for API keys
├── .gitignore
├── pyproject.toml               # Project config + dependencies
└── README.md
Architecture Decisions

1. Module interface
Every module follows one pattern:

class DnsIntelModule(BaseModule):
    name = "dns_intel"
    phase = 1
    
    async def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        # Do work, populate context with raw data, return findings
Each module can also run standalone: python -m argus.modules.dns_intel true-fruits.com

2. ScanContext — shared mutable state
A Pydantic model that accumulates results as modules run. Phase 2 modules read IPs discovered by Phase 1. Phase 3 reads subdomains from Phase 2. No race conditions because the orchestrator controls execution order within phases.

3. Sync DNS, async HTTP
dnspython is synchronous — wrap in asyncio.to_thread() where needed. HTTP requests use aiohttp for parallel fetching within a module (e.g., checking 40 file paths concurrently with a semaphore).

4. Graceful degradation
Every module wrapped in try/except at the orchestrator level. Failed module → log warning, continue. Partial results always saved after each phase.

5. Personalization for Instantly
The CSV summary includes a personalization_snippet column — a ready-to-paste HTML block with the top 1-3 findings formatted for cold email. This plugs directly into Instantly’s personalization variables.

Example: "Ihr Exchange 2019 ist End-of-Life (CU14, Apr 2026 ESU abgelaufen). Ihre AD-Domain 'truefruits.local' ist über NTLM Challenge öffentlich sichtbar. Ihr GF Marco Knauf taucht in 3 Datenlecks auf."

Build Order — 10 Steps

Step 1: DNS Foundation + Scoring (THIS SESSION)
Modules: M01 (DNS Intel), M26 (Zone Transfer), M28 (DNSSEC), M32 (CAA), M33 (WHOIS), M16 (Scoring)
Why first: Zero dependencies, no API keys needed, instantly produces valuable findings
Files to create:

pyproject.toml — project metadata + all dependencies
.env.example — API key template
.gitignore
argus/__init__.py, __main__.py, cli.py
argus/config.py — pydantic-settings
argus/models.py — Finding, ScanContext, ScanResult, DNSResult, Severity
argus/modules/base.py — BaseModule ABC
argus/modules/__init__.py — registry
argus/modules/dns_intel.py — Full DNS: A, MX, SPF, DMARC, DKIM (18 selectors), MTA-STS, DANE, BIMI, NS, TXT → 10 finding types
argus/modules/zone_transfer.py — AXFR test → 1 finding type (CRITICAL)
argus/modules/dnssec.py — DNSKEY check → 1 finding type
argus/modules/caa.py — CAA check → 1 finding type
argus/modules/whois_check.py — Expiration check → 1 finding type
argus/scoring.py — Weighted scoring engine
argus/scanner.py — Orchestrator (runs Step 1 modules, outputs JSON)
tests/test_dns_intel.py, tests/test_scoring.py
Verification:

pip install -e .
python -m argus scan --domain true-fruits.com
cat results/true-fruits.com.json | python -m json.tool
# Should show: SPF/DMARC/DKIM findings, exposure score, all DNS data
Step 2: HTTP Checks
Modules: M09 (File Exposure), M05 (Headers), M24 (CORS), M30 (Source Maps)
Depends on: Step 1 (needs discovered hosts)

Step 3: Exchange + Certificates
Modules: M08 (Exchange/NTLM), M25 (Cert SANs)
The “woah” modules — AD domain leak, internal hostnames

Step 4: Shodan Enrichment
Modules: M04 (Shodan), M27 (Favicon Hash)
Needs: Shodan API key ($49/mo)

Step 5: Subdomains
Modules: M02 (crt.sh + DNS), M31 (Takeover Detection)
Note: Move this earlier than spec suggests — subdomains feed into Steps 2-4

Step 6: Credential Exposure
Modules: M12 (HIBP)
Needs: HIBP API key ($3.50/mo)

Step 7: Historical Intel
Modules: M29 (GitHub Secrets), M30 (Wayback Machine)
The “heilige Scheiße” modules

Step 8: Google + Cloud
Modules: M23 (Google Dorking), M33 (Cloud Buckets)
Needs: SerpAPI key ($50/mo)

Step 9: Intelligence Layer
Modules: M07, M29 (GraphQL), M13, M14, M15

Step 10: Analysis + Output
Modules: M17 (LLM Attack Path), M18 (NIS2), M19 (Reports/Emails), full orchestrator with CSV summary + personalization column

Step 1 Implementation Detail

Models (argus/models.py)
Severity: KRITISCH, HOCH, MITTEL, NIEDRIG, INFO
Finding: id, module, category, title, description, severity, evidence, nis2_paragraphs, remediation, cvss_score?, cve_ids
DNSResult: mx_records, spf_record, spf_mechanism, spf_includes, dmarc_record, dmarc_policy, dmarc_subdomain_policy, dkim_selectors_found, dkim_selectors_checked, mta_sts, dane_tlsa, bimi, ns_records, ns_provider, txt_records, a_records
ScanContext: domain, company_name, dns (DNSResult), findings (list), discovered_ips (set), subdomains, mx_hosts, etc.
ScanResult: domain, company_name, scan_timestamp, dns, findings, exposure_score, score_breakdown, nis2_compliance, scan_duration_seconds
DNS Intel Module (dns_intel.py) — 10 Finding Types
ID	Condition	Severity
DNS-001	SPF ~all or ?all	HOCH
DNS-002	No SPF	KRITISCH
DNS-003	No DKIM (18 selectors checked)	HOCH
DNS-004	DMARC p=none	HOCH
DNS-005	DMARC sp=none while p!=none	HOCH
DNS-006	No DMARC	KRITISCH
DNS-007	No MTA-STS	MITTEL
DNS-008	No DANE/TLSA	MITTEL
DNS-009	No BIMI	NIEDRIG
DNS-010	SPF >10 lookups	MITTEL
Scoring Engine (scoring.py)
Weights: email_security 20%, infrastructure 25%, web_application 20%, credential_exposure 15%, exchange_exposure 10%, supply_chain 10%
Severity points: KRITISCH=25, HOCH=15, MITTEL=8, NIEDRIG=3, INFO=0
Step 1 only populates email_security — other categories filled as modules are added.

CLI (cli.py)
python -m argus scan --domain DOMAIN          # Single domain
python -m argus scan --input leads.csv        # Batch from CSV
python -m argus scan --domain DOMAIN --steps 1  # Only Step 1 modules
Challenging the “Personalization Column” Idea

Verdict: Excellent idea, implement it. Here’s how to make it 10x:

The _summary.csv gets these columns for Instantly:

domain, company_name, score, findings_critical, findings_high, findings_total
top_finding_1, top_finding_2, top_finding_3 — individual columns so Instantly can reference {{top_finding_1}} etc.
personalization_block — all top findings as one formatted block for the email body
msp_name — enables “Ihr MSP {msp_name} hat grundlegende Konfigurationen nicht umgesetzt” angle
subject_line — pre-generated email subject: “{company_name} — {top_finding_1_short}”
This turns the CSV into a plug-and-play Instantly import. Zero manual work between scan and campaign launch.
