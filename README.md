# KENGO ARGUS

Automated passive reconnaissance engine for German Mittelstand cybersecurity. Scans company domains from the outside to find specific, verifiable vulnerabilities that drive outbound sales.

28 modules. 100+ finding types. Zero interaction required.

## What it does

Point it at a domain. It runs 28 passive recon modules across 10 steps, produces an exposure score (0-100), maps findings to NIS2 compliance, generates a German-language attack narrative, and outputs an HTML report + Instantly-ready CSV.

```bash
python -m argus scan --domain true-fruits.com --company "true fruits"
```

Example output: 36 findings, score 44/100, 8 critical, 5 technologies detected, NIS2 compliance mapped, HTML report generated. ~4 minutes.

## Modules

| Step | Modules | What they find |
|------|---------|---------------|
| 1 | DNS Intel, DNSSEC, CAA, WHOIS, Zone Transfer | SPF/DMARC/DKIM gaps, email security, domain hygiene |
| 2 | HTTP Headers, File Exposure, CORS, Source Maps | Missing security headers, exposed .env/.git, CORS misconfig |
| 3 | Exchange/NTLM, Certificate SANs | AD domain leak, internal hostnames, Exchange EOL |
| 4 | Shodan (InternetDB), Favicon Hash | Open ports, CVEs, hidden infrastructure |
| 5 | Ownership, Subdomain Discovery, Subdomain Takeover | Impressum parsing, crt.sh + DNS brute force, dangling CNAMEs |
| 6 | Credential Exposure (HIBP) | Employee emails in data breaches |
| 7 | GitHub Secrets, Wayback Machine | Leaked credentials on GitHub, historical file exposure |
| 8 | Google Dorking, Cloud Buckets | Indexed sensitive files, public S3/Azure/GCS buckets |
| 9 | Tech Fingerprint, GraphQL, MSP ID, Supply Chain | CMS/framework versions, schema exposure, third-party services |
| 10 | Attack Path (LLM), NIS2 Mapping, Report Gen | German attack narrative, NIS2 §30 traffic lights, HTML report |

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[all,dev]"
cp .env.example .env
# Fill in API keys (see below)
```

## API Keys

| Key | Used by | Cost | Required? |
|-----|---------|------|-----------|
| — | InternetDB (ports/CVEs) | Free, unlimited | No (built-in) |
| `SHODAN_API_KEY` | Favicon hash, paid enrichment | Free tier: 100/month | Optional |
| `HIBP_API_KEY` | Credential exposure | $3.50/month | Optional |
| `GITHUB_TOKEN` | GitHub secret scanning | Free | Optional |
| `SERPAPI_KEY` | Google dorking | Free tier: 100/month | Optional |
| `ANTHROPIC_API_KEY` | Attack path narrative | Usage-based | Optional |

Every API-dependent module skips gracefully when its key is absent. The scanner always runs.

## Usage

```bash
# Single domain
python -m argus scan --domain example.com --company "Example GmbH"

# Batch scan from CSV (columns: domain, company_name, gf_name, gf_email)
python -m argus scan --input leads.csv --output results

# Only run steps 1-5 (no API keys needed)
python -m argus scan --domain example.com --steps 5

# Force rescan
python -m argus scan --domain example.com --force

# Verbose logging
python -m argus scan --domain example.com --verbose
```

## Output

- `results/{domain}.json` — Full scan data (findings, scores, technologies, NIS2, attack path)
- `results/{domain}.html` — Customer-facing HTML report
- `results/_summary.csv` — Instantly-ready CSV with personalization columns

CSV columns for Instantly: `domain`, `company_name`, `exposure_score`, `findings_critical`, `findings_high`, `findings_total`, `top_finding_1`, `top_finding_2`, `top_finding_3`, `personalization_block`, `subject_line`

## Project Structure

```
argus/
├── __init__.py, __main__.py, cli.py    # Entry points
├── config.py                           # API keys + settings via pydantic-settings
├── models.py                           # Finding, ScanContext, ScanResult, Severity
├── scanner.py                          # Orchestrator — runs modules in phase order
├── scoring.py                          # Weighted exposure score (6 categories)
├── modules/
│   ├── base.py                         # BaseModule ABC
│   ├── __init__.py                     # @register decorator + auto-discovery
│   ├── dns_intel.py                    # Step 1: SPF/DMARC/DKIM/MTA-STS/DANE/BIMI
│   ├── dnssec.py, caa.py, whois_check.py, zone_transfer.py  # Step 1
│   ├── http_headers.py, file_exposure.py, cors.py, source_maps.py  # Step 2
│   ├── exchange.py, cert_san.py        # Step 3
│   ├── shodan_lookup.py, favicon_hash.py  # Step 4
│   ├── ownership.py, subdomain_discovery.py, subdomain_takeover.py  # Step 5
│   ├── credential_exposure.py          # Step 6
│   ├── github_secrets.py, wayback_machine.py  # Step 7
│   ├── google_dorking.py, cloud_buckets.py  # Step 8
│   ├── tech_fingerprint.py, graphql_introspection.py  # Step 9
│   ├── msp_identification.py, supply_chain.py  # Step 9
│   ├── attack_path.py, nis2_mapping.py, report_gen.py  # Step 10
│   └── (28 modules total)
└── templates/
    └── report.html.j2                  # HTML report template
```

## Tests

```bash
pytest tests/ -v
```

## Docs

- [Full Specification](docs/KENGO_ARGUS_SPEC.md) — 29-module spec with finding types, API details, scoring
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) — 10-step build order with architecture decisions
