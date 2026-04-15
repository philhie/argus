"""Tests for M03: IP Resolution & Cloud Provider."""

from unittest.mock import patch

from argus.models import ScanContext
from argus.modules.ip_cloud_provider import (
    identify_provider,
    reverse_dns_provider,
    scan_ip_cloud,
)


class TestIdentifyProvider:
    def test_aws_ip(self):
        assert identify_provider("52.94.1.1") == "AWS"

    def test_hetzner_ip(self):
        assert identify_provider("159.69.100.50") == "Hetzner"

    def test_azure_ip(self):
        assert identify_provider("20.50.0.1") == "Azure"

    def test_google_cloud_ip(self):
        assert identify_provider("34.120.0.1") == "Google Cloud"

    def test_cloudflare_ip(self):
        assert identify_provider("104.16.0.1") == "Cloudflare"

    def test_ionos_ip(self):
        assert identify_provider("212.227.100.1") == "IONOS"

    def test_strato_ip(self):
        assert identify_provider("85.214.50.1") == "Strato"

    def test_ovh_ip(self):
        assert identify_provider("51.68.10.1") == "OVH"

    def test_ovh_ip_not_misclassified_as_aws(self):
        """OVH 54.36.0.0/16 must match before AWS 54.0.0.0/8."""
        assert identify_provider("54.36.1.1") == "OVH"

    def test_azure_ip_not_misclassified_as_aws(self):
        """Azure 52.224.0.0/11 must match before AWS 52.0.0.0/8."""
        assert identify_provider("52.224.1.1") == "Azure"

    def test_unknown_ip(self):
        assert identify_provider("192.168.1.1") is None

    def test_invalid_ip(self):
        assert identify_provider("not-an-ip") is None


class TestReverseDnsProvider:
    @patch("argus.modules.ip_cloud_provider.socket.gethostbyaddr")
    def test_aws_ptr(self, mock_rdns):
        mock_rdns.return_value = ("ec2-1-2-3-4.compute-1.amazonaws.com", [], [])
        provider, hostname = reverse_dns_provider("1.2.3.4")
        assert provider == "AWS"
        assert "amazonaws.com" in hostname

    @patch("argus.modules.ip_cloud_provider.socket.gethostbyaddr")
    def test_hetzner_ptr(self, mock_rdns):
        mock_rdns.return_value = ("static.1.2.3.4.clients.your-server.hetzner.com", [], [])
        provider, hostname = reverse_dns_provider("1.2.3.4")
        assert provider == "Hetzner"

    @patch("argus.modules.ip_cloud_provider.socket.gethostbyaddr")
    def test_unknown_ptr(self, mock_rdns):
        mock_rdns.return_value = ("host.example.com", [], [])
        provider, hostname = reverse_dns_provider("1.2.3.4")
        assert provider is None
        assert hostname == "host.example.com"

    @patch("argus.modules.ip_cloud_provider.socket.gethostbyaddr")
    def test_no_ptr(self, mock_rdns):
        import socket
        mock_rdns.side_effect = socket.herror("Host not found")
        provider, hostname = reverse_dns_provider("1.2.3.4")
        assert provider is None
        assert hostname is None


class TestScanIpCloud:
    def test_empty_ips(self):
        ctx = ScanContext(domain="example.com")
        findings = scan_ip_cloud(ctx)
        assert findings == []

    @patch("argus.modules.ip_cloud_provider.reverse_dns_provider")
    def test_single_provider(self, mock_rdns):
        mock_rdns.return_value = (None, "host.example.com")
        ctx = ScanContext(domain="example.com")
        ctx.discovered_ips = {"52.94.1.1"}
        findings = scan_ip_cloud(ctx)

        assert ctx.cloud_providers == {"52.94.1.1": "AWS"}
        # Should have IP-001 finding for AWS
        assert any("IP-001" in f.id for f in findings)
        assert any("AWS" in f.title for f in findings)
        # Should NOT have IP-002 (only 1 provider)
        assert not any("IP-002" in f.id for f in findings)

    @patch("argus.modules.ip_cloud_provider.reverse_dns_provider")
    def test_multiple_providers(self, mock_rdns):
        mock_rdns.return_value = (None, "host.example.com")
        ctx = ScanContext(domain="example.com")
        ctx.discovered_ips = {"52.94.1.1", "159.69.100.50"}
        findings = scan_ip_cloud(ctx)

        assert len(ctx.cloud_providers) == 2
        # Should have IP-002 finding (multiple providers)
        assert any("IP-002" in f.id for f in findings)

    @patch("argus.modules.ip_cloud_provider.reverse_dns_provider")
    def test_no_rdns_finding(self, mock_rdns):
        mock_rdns.return_value = (None, None)  # No PTR record
        ctx = ScanContext(domain="example.com")
        ctx.discovered_ips = {"192.168.1.1"}  # Unknown IP, no rDNS
        findings = scan_ip_cloud(ctx)

        assert any("IP-003" in f.id for f in findings)
