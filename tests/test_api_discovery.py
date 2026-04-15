"""Tests for M11: API Endpoint Discovery."""

from unittest.mock import MagicMock, patch

from argus.models import Severity
from argus.modules.api_discovery import (
    API_PATHS,
    _has_markers,
    _is_soft_404,
    _looks_like_api_content,
    check_api_endpoints,
)


class TestSoft404Detection:
    def test_page_not_found(self):
        assert _is_soft_404("Page Not Found") is True

    def test_german_404(self):
        assert _is_soft_404("Seite nicht gefunden") is True

    def test_real_content(self):
        assert _is_soft_404('{"openapi": "3.0.0", "paths": {}}') is False


class TestHasMarkers:
    def test_swagger_markers(self):
        text = '<html><div id="swagger-ui"></div></html>'
        assert _has_markers(text, ["swagger-ui", "Swagger UI"]) is True

    def test_openapi_json_markers(self):
        text = '{"openapi": "3.0.0", "paths": {"/api": {}}}'
        assert _has_markers(text, ['"openapi"', '"paths"']) is True

    def test_no_match(self):
        text = "<html>Hello World</html>"
        assert _has_markers(text, ["swagger-ui", "Swagger UI"]) is False

    def test_empty_markers_always_true(self):
        assert _has_markers("anything", []) is True


class TestLooksLikeApiContent:
    def test_valid_swagger(self):
        resp = MagicMock()
        resp.content = b'{"openapi": "3.0.0", "paths": {}}' + b"x" * 100
        resp.text = '{"openapi": "3.0.0", "paths": {}}' + "x" * 100
        check = {"markers": ['"openapi"', '"paths"']}
        assert _looks_like_api_content(resp, check) is True

    def test_soft_404(self):
        resp = MagicMock()
        resp.content = b"Page Not Found" + b"x" * 100
        resp.text = "Page Not Found" + "x" * 100
        check = {"markers": ['"openapi"']}
        assert _looks_like_api_content(resp, check) is False

    def test_empty_response(self):
        resp = MagicMock()
        resp.content = b""
        resp.text = ""
        check = {"markers": []}
        assert _looks_like_api_content(resp, check) is False

    def test_no_markers_match(self):
        resp = MagicMock()
        resp.content = b"<html>Regular page</html>" + b"x" * 100
        resp.text = "<html>Regular page</html>" + "x" * 100
        check = {"markers": ['"openapi"', '"paths"']}
        assert _looks_like_api_content(resp, check) is False


class TestExcludedPaths:
    """Verify paths that overlap with file_exposure.py and graphql_introspection.py."""

    def test_swagger_excluded(self):
        paths = [p["path"] for p in API_PATHS]
        assert "/swagger" not in paths

    def test_swagger_ui_excluded(self):
        paths = [p["path"] for p in API_PATHS]
        assert "/swagger-ui" not in paths

    def test_api_docs_excluded(self):
        paths = [p["path"] for p in API_PATHS]
        assert "/api-docs" not in paths

    def test_graphiql_excluded(self):
        paths = [p["path"] for p in API_PATHS]
        assert "/graphiql" not in paths

    def test_graphql_excluded(self):
        paths = [p["path"] for p in API_PATHS]
        assert "/graphql" not in paths


class TestActuatorSeverity:
    """Verify actuator severity escalation."""

    def test_env_is_high(self):
        env_check = next(p for p in API_PATHS if p["path"] == "/actuator/env")
        assert env_check["severity"] == Severity.HIGH

    def test_beans_is_high(self):
        beans_check = next(p for p in API_PATHS if p["path"] == "/actuator/beans")
        assert beans_check["severity"] == Severity.HIGH

    def test_health_is_low(self):
        health_check = next(p for p in API_PATHS if p["path"] == "/actuator/health")
        assert health_check["severity"] == Severity.LOW

    def test_configprops_is_high(self):
        cp_check = next(p for p in API_PATHS if p["path"] == "/actuator/configprops")
        assert cp_check["severity"] == Severity.HIGH


class TestCheckApiEndpoints:
    @patch("argus.modules.api_discovery.requests.get")
    def test_swagger_ui_found(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b'<html><div id="swagger-ui">Swagger UI</div></html>' + b"x" * 100
        resp.text = '<html><div id="swagger-ui">Swagger UI</div></html>' + "x" * 100
        mock_get.return_value = resp

        findings = check_api_endpoints("https://example.com")
        assert len(findings) > 0
        assert all(f.category == "web_application" for f in findings)

    @patch("argus.modules.api_discovery.requests.get")
    def test_404_no_findings(self, mock_get):
        resp = MagicMock()
        resp.status_code = 404
        resp.content = b"Not Found"
        resp.text = "Not Found"
        mock_get.return_value = resp

        findings = check_api_endpoints("https://example.com")
        assert findings == []

    @patch("argus.modules.api_discovery.requests.get")
    def test_actuator_env_high_severity(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.content = b'{"propertySources": [], "activeProfiles": []}' + b"x" * 100
        resp.text = '{"propertySources": [], "activeProfiles": []}' + "x" * 100
        mock_get.return_value = resp

        findings = check_api_endpoints("https://example.com")
        actuator_env = [f for f in findings if "/actuator/env" in f.evidence]
        if actuator_env:
            assert actuator_env[0].severity == Severity.HIGH
