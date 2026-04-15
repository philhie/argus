# Changelog

All notable changes to KENGO ARGUS will be documented in this file.

## [0.3.0.0] - 2026-04-15

### Added
- **M03: IP Resolution & Cloud Provider** — maps discovered IPs to AWS, Azure, Google Cloud, Hetzner, IONOS, OVH, Strato, Oracle Cloud, DigitalOcean, Cloudflare using CIDR ranges with reverse DNS fallback. Stores provider mapping in ScanContext for downstream modules.
- **M06: TLS Analysis** — probes TLS 1.0/1.1/1.3 support and detects weak cipher suites (RC4, DES, 3DES/SWEET32, NULL, EXPORT). Checks domain, MX hosts, and subdomains. Complements cert_san.py (which handles SANs, expiry, self-signed).
- **M10: Admin Panel Discovery** — enumerates 18 common admin paths (WordPress, TYPO3, Joomla, Drupal, phpMyAdmin, Adminer, cPanel, Plesk) with soft-404 detection. 403 responses reported at INFO severity (confirms path exists).
- **M11: API Endpoint Discovery** — probes 21 API documentation and health endpoints (Swagger/OpenAPI variants, ReDoc, Spring Actuator, REST APIs). Content marker validation prevents false positives. Actuator sensitive endpoints (env, beans, configprops) escalated to HIGH severity.
- `cloud_providers` field on ScanContext for IP-to-provider mapping
- Unit tests for all 4 new modules (58 new tests, 96 total)
- Scanner now registers 32 modules (was 28)

### Technical Notes
- CIDR ranges sorted by prefix length (most specific first) to prevent misclassification of overlapping ranges
- M10 excludes paths already in file_exposure.py (/server-status, /server-info)
- M11 excludes paths already in file_exposure.py (/swagger, /swagger-ui, /api-docs) and graphql_introspection.py (/graphql, /graphiql)
- TLS 1.0/1.1 probing requires OpenSSL (LibreSSL on macOS has removed support — module degrades gracefully)

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
