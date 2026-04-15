# Changelog

All notable changes to KENGO ARGUS will be documented in this file.

## [0.2.0.0] - 2026-04-15

### Added
- Steps 4-10: 17 new modules bringing the total to 28
- **Shodan InternetDB integration** (free, unlimited) as primary port/CVE data source — paid Shodan API now optional enrichment only
- **Subdomain discovery** via crt.sh Certificate Transparency + DNS brute force (~100 common German subdomains)
- **Subdomain takeover detection** — checks dangling CNAMEs against 15 service fingerprints (GitHub Pages, Heroku, Azure, S3, etc.)
- **Impressum/ownership parsing** — extracts company info, executive names, and emails from German Impressum pages
- **HIBP credential exposure** — checks employee emails against Have I Been Pwned breach database
- **GitHub secret scanning** — searches public repos for leaked credentials related to the domain (12 dork patterns)
- **Wayback Machine historical exposure** — finds historically exposed .env, .sql, .git, admin panels via CDX API
- **Google dorking** via SerpAPI — 12 dork queries for indexed sensitive files
- **Cloud bucket enumeration** — tests S3/Azure/GCS bucket name patterns for public access
- **Technology fingerprinting** — Wappalyzer-style detection of CMS, frameworks, libraries (~40 signatures)
- **GraphQL introspection** — tests 5 common endpoints for schema exposure
- **MSP identification** — identifies managed service providers from DNS patterns (~20 German IT providers)
- **Supply chain mapping** — extracts third-party services from HTML (22 known services)
- **NIS2 compliance mapping** — maps all findings to NIS2 §30 Abs. 2 Nr. 1-10 with traffic-light scoring
- **LLM attack path narrative** — Claude generates German attack scenarios from findings
- **HTML report generation** — customer-facing report with exposure score, NIS2 traffic lights, findings table
- README.md with full documentation

### Changed
- Shodan module now uses InternetDB as primary (free, no auth) with paid API as optional enrichment
- NIS2 mapping uses per-finding annotations as primary source, prefix matching as fallback
- Report findings sorted by severity (CRITICAL first) instead of alphabetical

### Fixed
- S3 bucket false-positive: non-listable buckets no longer classified as "listable"
- Wayback Machine sitemap regex that could never match
- MSP secondary findings now use MSP-002 instead of duplicate MSP-001
- Tech fingerprint German text uses proper umlauts

## [0.1.0.0] - 2026-04-15

### Added
- ARGUS passive reconnaissance scanner with 11 modules across 3 build steps
- DNS Intelligence: SPF, DMARC, DKIM (25 selectors including German ESPs), MTA-STS, DANE, BIMI, NS analysis with 10 finding types
- DNS auxiliary modules: Zone Transfer (AXFR) test, DNSSEC validation, CAA records, WHOIS expiration monitoring
- HTTP security: headers check (HSTS, CSP, X-Frame-Options, cookie flags), file exposure (28 sensitive paths), CORS misconfiguration, JS source map detection
- Exchange detection with NTLM challenge: AD domain extraction, server FQDN leak, version/EOL detection, endpoint enumeration (9 paths), auth method analysis
- Certificate SAN analysis: internal hostname and private IP leak detection
- Weighted scoring engine across 6 categories (email, infrastructure, web, credentials, exchange, supply chain)
- CLI with single-domain (`--domain`) and batch CSV (`--input`) modes
- Instantly-ready CSV output with personalization columns (top_finding_1/2/3, personalization_block, subject_line)
- Config flags for legally sensitive modules (enable_axfr, enable_ntlm)
- Auto-discovery module registry (pkgutil-based, no manual imports needed)
- Full technical specification and implementation plan in docs/
