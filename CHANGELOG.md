# Changelog

All notable changes to KENGO ARGUS will be documented in this file.

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
