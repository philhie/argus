"""Tests for DNS Intel module finding generation logic."""

from argus.models import DNSResult, Finding, Severity
from argus.modules.dns_intel import (
    _count_spf_lookups,
    _extract_dmarc_tag,
    _extract_spf_mechanism,
)


def test_extract_spf_hardfail():
    assert _extract_spf_mechanism("v=spf1 include:example.com -all") == "-all"


def test_extract_spf_softfail():
    assert _extract_spf_mechanism("v=spf1 include:example.com ~all") == "~all"


def test_extract_spf_neutral():
    assert _extract_spf_mechanism("v=spf1 include:example.com ?all") == "?all"


def test_extract_spf_no_mechanism():
    assert _extract_spf_mechanism("v=spf1 include:example.com") is None


def test_extract_dmarc_policy():
    record = "v=DMARC1; p=quarantine; sp=none; adkim=s"
    assert _extract_dmarc_tag(record, "p") == "quarantine"
    assert _extract_dmarc_tag(record, "sp") == "none"
    assert _extract_dmarc_tag(record, "adkim") == "s"


def test_extract_dmarc_missing_tag():
    record = "v=DMARC1; p=reject"
    assert _extract_dmarc_tag(record, "sp") is None
    assert _extract_dmarc_tag(record, "rua") is None


def test_count_spf_lookups_simple():
    spf = "v=spf1 include:_spf.google.com include:servers.mcsv.net -all"
    assert _count_spf_lookups(spf) == 2


def test_count_spf_lookups_with_mx_and_a():
    spf = "v=spf1 mx a include:example.com redirect=other.com -all"
    assert _count_spf_lookups(spf) == 4  # mx + a + include + redirect


def test_count_spf_lookups_ip_only():
    spf = "v=spf1 ip4:1.2.3.4 ip6:::1 -all"
    assert _count_spf_lookups(spf) == 0  # IPs don't count as lookups
