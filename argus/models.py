"""Core data models for KENGO ARGUS scanner."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "KRITISCH"
    HIGH = "HOCH"
    MEDIUM = "MITTEL"
    LOW = "NIEDRIG"
    INFO = "INFO"


class Finding(BaseModel):
    """A single security finding with evidence."""

    id: str  # e.g. "DNS-001", "EX-003"
    module: str  # which module produced this
    category: str  # "email_security", "infrastructure", "web_application", etc.
    title: str  # German, concise
    description: str = ""  # German, 2-3 sentences
    severity: Severity
    evidence: str  # The exact command or data that proves it
    evidence_raw: Optional[str] = None  # Raw response data
    nis2_paragraphs: list[str] = Field(default_factory=list)
    remediation: str = ""  # German, actionable
    cvss_score: Optional[float] = None
    cve_ids: list[str] = Field(default_factory=list)


class MXRecord(BaseModel):
    priority: int
    host: str
    ip: Optional[str] = None
    mail_type: Optional[str] = None  # "exchange_online", "google", "on_prem", "relay"


class ARecord(BaseModel):
    ip: str
    provider: Optional[str] = None


class DNSResult(BaseModel):
    """Full DNS analysis result for a domain."""

    a_records: list[ARecord] = Field(default_factory=list)
    mx_records: list[MXRecord] = Field(default_factory=list)

    # SPF
    spf_record: Optional[str] = None
    spf_mechanism: Optional[str] = None  # ~all, -all, ?all, +all
    spf_includes: list[str] = Field(default_factory=list)
    spf_ips: list[str] = Field(default_factory=list)
    spf_lookup_count: int = 0

    # DMARC
    dmarc_record: Optional[str] = None
    dmarc_policy: Optional[str] = None  # none, quarantine, reject
    dmarc_subdomain_policy: Optional[str] = None
    dmarc_alignment_dkim: Optional[str] = None
    dmarc_alignment_spf: Optional[str] = None

    # DKIM
    dkim_selectors_found: list[str] = Field(default_factory=list)
    dkim_selectors_checked: list[str] = Field(default_factory=list)

    # Advanced email security
    mta_sts: bool = False
    dane_tlsa: bool = False
    bimi: bool = False

    # Nameservers
    ns_records: list[str] = Field(default_factory=list)
    ns_provider: Optional[str] = None

    # All TXT records
    txt_records: list[str] = Field(default_factory=list)

    # DNSSEC
    dnssec_enabled: bool = False

    # CAA
    caa_records: list[str] = Field(default_factory=list)

    # Zone Transfer
    zone_transfer_vulnerable: bool = False
    zone_transfer_records: list[dict[str, Any]] = Field(default_factory=list)

    # WHOIS
    whois_expiry_date: Optional[str] = None
    whois_days_until_expiry: Optional[int] = None
    whois_registrar: Optional[str] = None


class ScanContext(BaseModel):
    """Mutable shared state accumulated across modules during a scan."""

    domain: str
    company_name: str = ""
    gf_name: Optional[str] = None
    gf_email: Optional[str] = None

    # Phase 1 outputs
    dns: DNSResult = Field(default_factory=DNSResult)

    # Accumulated across phases
    discovered_ips: set[str] = Field(default_factory=set)
    cloud_providers: dict[str, str] = Field(default_factory=dict)  # IP → provider
    mx_hosts: list[str] = Field(default_factory=list)
    live_urls: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)

    # Steps 4-10 enrichment
    subdomains: list[str] = Field(default_factory=list)
    shodan_hosts: list[dict[str, Any]] = Field(default_factory=list)
    employee_emails: list[str] = Field(default_factory=list)
    technologies: list[dict[str, Any]] = Field(default_factory=list)
    msp_info: dict[str, Any] = Field(default_factory=dict)
    supply_chain_entries: list[dict[str, Any]] = Field(default_factory=list)
    ownership_info: dict[str, Any] = Field(default_factory=dict)
    attack_path_narrative: str = ""
    nis2_compliance: dict[str, str] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}


class ScoreBreakdown(BaseModel):
    email_security: int = 0
    infrastructure: int = 0
    web_application: int = 0
    credential_exposure: int = 0
    exchange_exposure: int = 0
    supply_chain: int = 0


class ScanResult(BaseModel):
    """Final output of a complete domain scan."""

    domain: str
    company_name: str
    scan_timestamp: str
    scan_duration_seconds: float = 0.0

    # Module data
    dns: DNSResult = Field(default_factory=DNSResult)

    # Analysis
    findings: list[Finding] = Field(default_factory=list)
    exposure_score: int = 0
    score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)

    # Counts
    findings_critical: int = 0
    findings_high: int = 0
    findings_total: int = 0

    # Personalization for Instantly
    top_finding_1: str = ""
    top_finding_2: str = ""
    top_finding_3: str = ""
    personalization_block: str = ""
    subject_line: str = ""

    # Steps 4-10 enrichment
    technologies: list[dict[str, Any]] = Field(default_factory=list)
    attack_path_narrative: str = ""
    nis2_compliance: dict[str, str] = Field(default_factory=dict)
