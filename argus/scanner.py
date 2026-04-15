"""Orchestrator — runs scanner modules in phase order for a domain."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone

from argus.config import settings
from argus.models import ScanContext, ScanResult, Severity
from argus.modules import get_modules_up_to_step
from argus.scoring import calculate_exposure_score

# Auto-discover and import all modules so they register themselves
import importlib
import pkgutil

import argus.modules as _modules_pkg

for _importer, _modname, _ispkg in pkgutil.iter_modules(_modules_pkg.__path__):
    if _modname not in ("base", "__init__"):
        importlib.import_module(f"argus.modules.{_modname}")

logger = logging.getLogger("argus")


def scan_domain(
    domain: str,
    company_name: str = "",
    gf_name: str | None = None,
    gf_email: str | None = None,
    max_step: int = 10,
) -> ScanResult:
    """Run all registered modules up to max_step for a single domain."""
    start_time = time.time()

    context = ScanContext(
        domain=domain,
        company_name=company_name or domain,
        gf_name=gf_name,
        gf_email=gf_email,
    )

    modules = get_modules_up_to_step(max_step)

    for module_cls in modules:
        module = module_cls()
        module_name = module.name
        try:
            findings = module.scan(domain, context)
            context.findings.extend(findings)
            logger.debug(f"  {module_name}: {len(findings)} findings")
        except Exception as e:
            logger.warning(f"  {module_name} FAILED: {e}")
            continue

    # Calculate score
    score, breakdown = calculate_exposure_score(context.findings)

    # Build personalization
    top_findings = sorted(
        context.findings,
        key=lambda f: (
            {Severity.CRITICAL: 4, Severity.HIGH: 3, Severity.MEDIUM: 2,
             Severity.LOW: 1, Severity.INFO: 0}[f.severity],
            len(f.evidence),
        ),
        reverse=True,
    )

    top_1 = top_findings[0].title if len(top_findings) > 0 else ""
    top_2 = top_findings[1].title if len(top_findings) > 1 else ""
    top_3 = top_findings[2].title if len(top_findings) > 2 else ""

    personalization_parts = [f.title for f in top_findings[:3]]
    personalization_block = " | ".join(personalization_parts) if personalization_parts else ""

    subject_line = f"{company_name or domain} — {top_1}" if top_1 else ""

    result = ScanResult(
        domain=domain,
        company_name=company_name or domain,
        scan_timestamp=datetime.now(timezone.utc).isoformat(),
        scan_duration_seconds=round(time.time() - start_time, 2),
        dns=context.dns,
        findings=context.findings,
        exposure_score=score,
        score_breakdown=breakdown,
        findings_critical=len([f for f in context.findings if f.severity == Severity.CRITICAL]),
        findings_high=len([f for f in context.findings if f.severity == Severity.HIGH]),
        findings_total=len(context.findings),
        top_finding_1=top_1,
        top_finding_2=top_2,
        top_finding_3=top_3,
        personalization_block=personalization_block,
        subject_line=subject_line,
    )

    return result


def save_result(result: ScanResult, output_dir: str | None = None) -> str:
    """Save scan result to JSON file. Returns the file path."""
    out_dir = output_dir or settings.output_dir
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, f"{result.domain}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False, default=str)

    return filepath
