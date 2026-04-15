"""Tests for M10: Admin Panel Discovery."""

from unittest.mock import MagicMock, patch

from argus.models import Severity
from argus.modules.admin_panel import (
    ADMIN_PATHS,
    _is_soft_404,
    _looks_like_real_content,
    check_admin_panels,
)


class TestSoft404Detection:
    def test_page_not_found(self):
        assert _is_soft_404("Page Not Found - Example") is True

    def test_german_404(self):
        assert _is_soft_404("Seite nicht gefunden") is True

    def test_404_number(self):
        assert _is_soft_404("Error 404 - Not Found") is True

    def test_real_content(self):
        assert _is_soft_404("Welcome to the admin dashboard") is False

    def test_oops_page(self):
        assert _is_soft_404("Oops! Something went wrong") is True


class TestLooksLikeRealContent:
    def test_empty_response(self):
        resp = MagicMock()
        resp.content = b""
        resp.text = ""
        assert _looks_like_real_content(resp) is False

    def test_tiny_response(self):
        resp = MagicMock()
        resp.content = b"OK"
        resp.text = "OK"
        assert _looks_like_real_content(resp) is False

    def test_soft_404_response(self):
        resp = MagicMock()
        resp.content = b"x" * 200
        resp.text = "<html><body>Page Not Found</body></html>"
        assert _looks_like_real_content(resp) is False

    def test_real_admin_page(self):
        resp = MagicMock()
        resp.content = b"x" * 500
        resp.text = "<html><body>WordPress Admin Dashboard - Login</body></html>"
        assert _looks_like_real_content(resp) is True


class TestExcludedPaths:
    """Verify paths that overlap with file_exposure.py are NOT in the list."""

    def test_server_status_excluded(self):
        paths = [p["path"] for p in ADMIN_PATHS]
        assert "/server-status" not in paths

    def test_server_info_excluded(self):
        paths = [p["path"] for p in ADMIN_PATHS]
        assert "/server-info" not in paths


class TestCheckAdminPanels:
    @patch("argus.modules.admin_panel.requests.get")
    def test_found_200(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b"<html>WordPress Admin Panel - Dashboard</html>" + b"x" * 100
        resp.text = "<html>WordPress Admin Panel - Dashboard</html>" + "x" * 100
        mock_get.return_value = resp

        findings = check_admin_panels("https://example.com")
        assert len(findings) > 0
        assert all(f.category == "web_application" for f in findings)
        assert all("§30 Abs. 2 Nr. 9" in f.nis2_paragraphs for f in findings)

    @patch("argus.modules.admin_panel.requests.get")
    def test_403_is_info_severity(self, mock_get):
        resp = MagicMock()
        resp.status_code = 403
        resp.content = b"Forbidden"
        resp.text = "Forbidden"
        resp.headers = {}
        mock_get.return_value = resp

        findings = check_admin_panels("https://example.com")
        # 403 findings should be INFO severity
        assert all(f.severity == Severity.INFO for f in findings)

    @patch("argus.modules.admin_panel.requests.get")
    def test_404_no_findings(self, mock_get):
        resp = MagicMock()
        resp.status_code = 404
        resp.content = b"Not Found"
        resp.text = "Not Found"
        mock_get.return_value = resp

        findings = check_admin_panels("https://example.com")
        assert findings == []

    @patch("argus.modules.admin_panel.requests.get")
    def test_redirect_to_login(self, mock_get):
        resp = MagicMock()
        resp.status_code = 302
        resp.content = b""
        resp.text = ""
        resp.headers = {"Location": "/wp-admin/login"}
        mock_get.return_value = resp

        findings = check_admin_panels("https://example.com")
        # Should detect the redirect to login as a found panel
        assert any("login" in f.evidence.lower() or "302" in f.evidence for f in findings)

    @patch("argus.modules.admin_panel.requests.get")
    def test_finding_ids_by_type(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b"<html>Admin Panel Content Here</html>" + b"x" * 100
        resp.text = "<html>Admin Panel Content Here</html>" + "x" * 100
        mock_get.return_value = resp

        findings = check_admin_panels("https://example.com")
        finding_ids = [f.id for f in findings]
        # Should have various ADMIN-* prefixed IDs
        assert all(f.id.startswith("ADMIN-") for f in findings)
