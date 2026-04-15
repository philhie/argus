"""Tests for M06: TLS Analysis."""

from argus.models import ScanContext
from argus.modules.tls_analysis import (
    _build_host_list,
    is_sweet32_cipher,
    is_weak_cipher,
)


class TestWeakCipherDetection:
    def test_rc4_is_weak(self):
        assert is_weak_cipher("TLS_RSA_WITH_RC4_128_SHA") is True

    def test_des_is_weak(self):
        assert is_weak_cipher("TLS_RSA_WITH_DES_CBC_SHA") is True

    def test_null_is_weak(self):
        assert is_weak_cipher("TLS_RSA_WITH_NULL_SHA") is True

    def test_export_is_weak(self):
        assert is_weak_cipher("TLS_RSA_EXPORT_WITH_RC4_40_MD5") is True

    def test_anon_is_weak(self):
        assert is_weak_cipher("TLS_DH_anon_WITH_AES_128_CBC_SHA") is True

    def test_aes_gcm_is_not_weak(self):
        assert is_weak_cipher("TLS_AES_256_GCM_SHA384") is False

    def test_chacha20_is_not_weak(self):
        assert is_weak_cipher("TLS_CHACHA20_POLY1305_SHA256") is False

    def test_ecdhe_aes_not_weak(self):
        assert is_weak_cipher("ECDHE-RSA-AES256-GCM-SHA384") is False


class TestSweet32Detection:
    def test_3des_is_sweet32(self):
        assert is_sweet32_cipher("TLS_RSA_WITH_3DES_EDE_CBC_SHA") is True

    def test_des_cbc3_is_sweet32(self):
        assert is_sweet32_cipher("DES-CBC3-SHA") is True

    def test_idea_is_sweet32(self):
        assert is_sweet32_cipher("TLS_RSA_WITH_IDEA_CBC_SHA") is True

    def test_aes_not_sweet32(self):
        assert is_sweet32_cipher("TLS_AES_256_GCM_SHA384") is False


class TestBuildHostList:
    def test_domain_only(self):
        ctx = ScanContext(domain="example.com")
        hosts = _build_host_list("example.com", ctx)
        assert hosts == ["example.com"]

    def test_with_mx_hosts(self):
        ctx = ScanContext(domain="example.com")
        ctx.mx_hosts = ["mx1.example.com", "mx2.example.com"]
        hosts = _build_host_list("example.com", ctx)
        assert hosts == ["example.com", "mx1.example.com", "mx2.example.com"]

    def test_deduplication(self):
        ctx = ScanContext(domain="example.com")
        ctx.mx_hosts = ["example.com"]  # Same as domain
        ctx.subdomains = ["example.com", "sub.example.com"]
        hosts = _build_host_list("example.com", ctx)
        assert hosts == ["example.com", "sub.example.com"]

    def test_caps_at_limits(self):
        ctx = ScanContext(domain="example.com")
        ctx.mx_hosts = [f"mx{i}.example.com" for i in range(10)]
        ctx.subdomains = [f"sub{i}.example.com" for i in range(20)]
        hosts = _build_host_list("example.com", ctx)
        # 1 domain + 3 mx + 5 subdomains = 9 max
        assert len(hosts) <= 9
