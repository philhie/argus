"""M19: HTML Report & CSV Generation.

Phase 6, Step 10. No API key required — file output only.

Usage: python -m argus.modules.report_gen example.com
"""

from __future__ import annotations

import csv
import io
import logging
import os
from pathlib import Path

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.report_gen")

# Severity sort order for consistent ranking
_SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFO: 4,
}

# CSV header columns
CSV_COLUMNS = [
    "domain",
    "company_name",
    "exposure_score",
    "findings_critical",
    "findings_high",
    "findings_total",
    "top_finding_1",
    "top_finding_2",
    "top_finding_3",
    "personalization_block",
    "subject_line",
]


def _build_result_dict(context: ScanContext) -> dict:
    """Build a ScanResult-like dict from the scan context for template rendering."""
    from argus.scoring import calculate_exposure_score

    score, breakdown = calculate_exposure_score(context.findings)

    sorted_findings = sorted(
        context.findings,
        key=lambda f: (_SEVERITY_ORDER.get(f.severity, 99), -len(f.evidence)),
    )

    top_titles = [f.title for f in sorted_findings[:3]]

    # Pre-sort findings by severity (CRITICAL first) for the template
    all_findings_sorted = sorted(
        context.findings,
        key=lambda f: _SEVERITY_ORDER.get(f.severity, 99),
    )

    return {
        "domain": context.domain,
        "company_name": context.company_name or context.domain,
        "scan_timestamp": "",
        "scan_duration_seconds": 0.0,
        "findings": all_findings_sorted,
        "exposure_score": score,
        "score_breakdown": breakdown,
        "findings_critical": len(
            [f for f in context.findings if f.severity == Severity.CRITICAL]
        ),
        "findings_high": len(
            [f for f in context.findings if f.severity == Severity.HIGH]
        ),
        "findings_total": len(context.findings),
        "technologies": context.technologies,
        "attack_path_narrative": context.attack_path_narrative,
        "nis2_compliance": context.nis2_compliance,
        "top_finding_1": top_titles[0] if len(top_titles) > 0 else "",
        "top_finding_2": top_titles[1] if len(top_titles) > 1 else "",
        "top_finding_3": top_titles[2] if len(top_titles) > 2 else "",
        "personalization_block": " | ".join(top_titles) if top_titles else "",
        "subject_line": (
            f"{context.company_name or context.domain} — {top_titles[0]}"
            if top_titles
            else ""
        ),
    }


def generate_html_report(context: ScanContext, output_dir: str) -> str | None:
    """Render HTML report from scan context. Returns file path or None on failure."""
    try:
        import jinja2
    except ImportError:
        logger.warning("jinja2 not installed — skipping HTML report generation")
        return None

    result_dict = _build_result_dict(context)

    # Use a SimpleNamespace so the template can access result.domain etc.
    from types import SimpleNamespace

    # Wrap findings so severity.value works in the template
    result_ns = SimpleNamespace(**result_dict)

    env = jinja2.Environment(
        loader=jinja2.PackageLoader("argus", "templates"),
        autoescape=jinja2.select_autoescape(["html"]),
    )
    template = env.get_template("report.html.j2")

    html = template.render(
        result=result_ns,
        nis2=context.nis2_compliance,
    )

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{context.domain}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info("HTML report written to %s", filepath)
    return filepath


def append_csv_row(context: ScanContext, output_dir: str) -> str:
    """Append a summary row to _summary.csv. Returns file path."""
    result_dict = _build_result_dict(context)

    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "_summary.csv")

    file_exists = os.path.isfile(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({col: result_dict.get(col, "") for col in CSV_COLUMNS})

    logger.info("CSV row appended to %s", csv_path)
    return csv_path


@register
class ReportGenModule(BaseModule):
    name = "report_gen"
    description = "HTML Report & CSV Generation"
    phase = 6
    step = 10

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        from argus.config import settings

        output_dir = settings.output_dir

        html_path = generate_html_report(context, output_dir)
        if html_path:
            logger.info("Report generated: %s", html_path)

        csv_path = append_csv_row(context, output_dir)
        logger.info("Summary CSV updated: %s", csv_path)

        return []


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.report_gen <domain>")
        sys.exit(1)

    target = sys.argv[1]
    print(f"Generating demo report for {target}...")

    # Build a demo context with sample findings
    demo_context = ScanContext(
        domain=target,
        company_name=target.split(".")[0].title(),
        technologies=[
            {"name": "Apache", "version": "2.4.51"},
            {"name": "WordPress", "version": "6.1"},
            {"name": "PHP", "version": "8.1"},
        ],
        attack_path_narrative=(
            "Ein Angreifer kann oeffentlich erreichbare Login-Seiten nutzen, "
            "um Brute-Force-Angriffe durchzufuehren. Fehlende DMARC-Policy "
            "ermoeglicht Phishing im Namen der Domain."
        ),
        nis2_compliance={
            "§30 Abs. 2 Nr. 1": "RED",
            "§30 Abs. 2 Nr. 2": "YELLOW",
            "§30 Abs. 2 Nr. 3": "GREEN",
            "§30 Abs. 2 Nr. 4": "YELLOW",
            "§30 Abs. 2 Nr. 5": "RED",
            "§30 Abs. 2 Nr. 6": "GRAY",
            "§30 Abs. 2 Nr. 7": "YELLOW",
            "§30 Abs. 2 Nr. 8": "RED",
            "§30 Abs. 2 Nr. 9": "GREEN",
            "§30 Abs. 2 Nr. 10": "YELLOW",
        },
    )

    # Add demo findings
    demo_context.findings = [
        Finding(
            id="DNS-001",
            module="dns_intel",
            category="email_security",
            title="DMARC-Policy fehlt",
            description="Keine DMARC-Policy konfiguriert.",
            severity=Severity.HIGH,
            evidence="Kein _dmarc TXT-Record gefunden",
            remediation="DMARC-Record mit Policy 'quarantine' oder 'reject' setzen.",
        ),
        Finding(
            id="HDR-002",
            module="http_headers",
            category="web_application",
            title="Strict-Transport-Security fehlt",
            description="HSTS-Header nicht gesetzt.",
            severity=Severity.MEDIUM,
            evidence="Header Strict-Transport-Security nicht vorhanden",
            remediation="HSTS-Header mit max-age >= 31536000 setzen.",
        ),
        Finding(
            id="CERT-001",
            module="cert_san",
            category="infrastructure",
            title="Zertifikat laeuft in 14 Tagen ab",
            severity=Severity.CRITICAL,
            evidence="Ablaufdatum: 2025-02-01",
            remediation="Zertifikat zeitnah erneuern.",
        ),
    ]

    output_dir = "results"
    html_path = generate_html_report(demo_context, output_dir)
    if html_path:
        print(f"HTML report: {html_path}")

    csv_path = append_csv_row(demo_context, output_dir)
    print(f"CSV summary: {csv_path}")
    print("Done.")
