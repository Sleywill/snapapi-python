"""
Unit tests for SnapAPI Python SDK — sync client.
HTTP calls are fully mocked via respx (httpx interceptor).
"""

from __future__ import annotations

import json
import pytest
import httpx
import respx

from snapapi import (
    SnapAPI,
    SnapAPIError,
    RateLimitError,
    AuthenticationError,
    ValidationError,
    QuotaExceededError,
)

BASE = "https://snapapi.pics"


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_client(**kwargs) -> SnapAPI:
    return SnapAPI(api_key="sk_test_1234", max_retries=0, **kwargs)


def json_response(data: dict, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json=data)


def binary_response(data: bytes = b"\x89PNG\r\n") -> httpx.Response:
    return httpx.Response(200, content=data, headers={"Content-Type": "image/png"})


# ── Constructor ───────────────────────────────────────────────────────────────

class TestConstructor:
    def test_raises_without_api_key(self):
        with pytest.raises(ValueError, match="api_key is required"):
            SnapAPI(api_key="")

    def test_trims_trailing_slash_from_base_url(self):
        snap = SnapAPI(api_key="k", base_url="https://example.com/")
        assert snap.base_url == "https://example.com"

    def test_default_values(self):
        snap = SnapAPI(api_key="k")
        assert snap.timeout == 60.0
        assert snap.max_retries == 3

    def test_context_manager(self):
        with SnapAPI(api_key="k") as snap:
            assert snap is not None


# ── screenshot() ─────────────────────────────────────────────────────────────

class TestScreenshot:
    def test_raises_without_input(self):
        snap = make_client()
        with pytest.raises(ValueError, match="url, html, or markdown"):
            snap.screenshot()

    @respx.mock
    def test_returns_bytes_for_binary_response(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        snap = make_client()
        result = snap.screenshot(url="https://example.com")
        assert isinstance(result, bytes)

    @respx.mock
    def test_returns_dict_when_storage_set(self):
        respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=json_response({"id": "f1", "url": "https://cdn.example.com/f1.png"})
        )
        snap = make_client()
        result = snap.screenshot(url="https://example.com", storage={"destination": "snapapi"})
        assert isinstance(result, dict)
        assert result["id"] == "f1"

    @respx.mock
    def test_sends_authorization_header(self):
        route = respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        snap = make_client()
        snap.screenshot(url="https://example.com")
        request = route.calls.last.request
        assert request.headers["Authorization"] == "Bearer sk_test_1234"


# ── pdf() ─────────────────────────────────────────────────────────────────────

class TestPdf:
    def test_raises_without_input(self):
        snap = make_client()
        with pytest.raises(ValueError, match="url or html"):
            snap.pdf()

    @respx.mock
    def test_returns_bytes(self):
        respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=httpx.Response(200, content=b"%PDF-1.4", headers={"Content-Type": "application/pdf"})
        )
        snap = make_client()
        result = snap.pdf(url="https://example.com")
        assert isinstance(result, bytes)
        assert result.startswith(b"%PDF")


# ── scrape() ─────────────────────────────────────────────────────────────────

class TestScrape:
    @respx.mock
    def test_returns_scrape_result(self):
        payload = {
            "success": True,
            "results": [{"page": 1, "url": "https://example.com", "data": "Hello world"}],
        }
        respx.post(f"{BASE}/v1/scrape").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.scrape(url="https://example.com")
        assert result.success is True
        assert result.results[0].data == "Hello world"


# ── extract() ────────────────────────────────────────────────────────────────

class TestExtract:
    @respx.mock
    def test_returns_extract_result(self):
        payload = {
            "success": True,
            "type": "markdown",
            "url": "https://example.com",
            "content": "# Title",
            "took": 1200,
            "cached": False,
        }
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.extract(url="https://example.com", type="markdown")
        assert result.content == "# Title"
        assert result.type == "markdown"


# ── quota() ──────────────────────────────────────────────────────────────────

class TestQuota:
    @respx.mock
    def test_returns_usage_result(self):
        payload = {"used": 42, "limit": 1000, "remaining": 958, "resetAt": "2026-04-01T00:00:00Z"}
        respx.get(f"{BASE}/v1/quota").mock(return_value=json_response(payload))
        snap = make_client()
        usage = snap.quota()
        assert usage.used == 42
        assert usage.remaining == 958


# ── og_image() ───────────────────────────────────────────────────────────────

class TestOgImage:
    @respx.mock
    def test_returns_bytes(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        snap = make_client()
        result = snap.og_image(url="https://example.com")
        assert isinstance(result, bytes)


# ── Error handling ────────────────────────────────────────────────────────────

class TestErrorHandling:
    @respx.mock
    def test_raises_authentication_error_on_401(self):
        respx.get(f"{BASE}/v1/ping").mock(
            return_value=json_response({"message": "Unauthorized", "error": "UNAUTHORIZED"}, status=401)
        )
        snap = make_client()
        with pytest.raises(AuthenticationError):
            snap.ping()

    @respx.mock
    def test_raises_rate_limit_error_on_429(self):
        respx.get(f"{BASE}/v1/ping").mock(
            return_value=httpx.Response(
                429,
                json={"message": "Too Many Requests"},
                headers={"Retry-After": "5"},
            )
        )
        snap = make_client()
        with pytest.raises(RateLimitError) as exc_info:
            snap.ping()
        assert exc_info.value.retry_after == 5.0

    @respx.mock
    def test_raises_validation_error_on_422(self):
        respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=json_response(
                {
                    "message": "Validation failed",
                    "error": "VALIDATION_ERROR",
                    "fields": {"url": "must be a valid URL"},
                },
                status=422,
            )
        )
        snap = make_client()
        with pytest.raises(ValidationError) as exc_info:
            snap.screenshot(url="not-a-url")
        assert "url" in exc_info.value.fields

    @respx.mock
    def test_raises_quota_exceeded_error_on_402(self):
        respx.get(f"{BASE}/v1/ping").mock(
            return_value=json_response(
                {"message": "quota exceeded", "error": "QUOTA_EXCEEDED"}, status=402
            )
        )
        snap = make_client()
        with pytest.raises(QuotaExceededError):
            snap.ping()

    @respx.mock
    def test_raises_snap_api_error_on_500(self):
        respx.get(f"{BASE}/v1/ping").mock(
            return_value=json_response({"message": "Internal Server Error"}, status=500)
        )
        snap = make_client()
        with pytest.raises(SnapAPIError) as exc_info:
            snap.ping()
        assert exc_info.value.status_code == 500


# ── Retry logic ───────────────────────────────────────────────────────────────

class TestRetryLogic:
    @respx.mock
    def test_retries_on_429_and_succeeds(self):
        call_count = 0

        def handler(request):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(
                    429,
                    json={"message": "rate limited"},
                    headers={"Retry-After": "0"},
                )
            return httpx.Response(200, json={"status": "ok", "timestamp": 1000})

        respx.get(f"{BASE}/v1/ping").mock(side_effect=handler)

        snap = SnapAPI(api_key="sk_test", max_retries=2, retry_delay=0.0)
        result = snap.ping()
        assert result["status"] == "ok"
        assert call_count == 2

    @respx.mock
    def test_retries_on_503_exhausts_max_retries(self):
        call_count = 0

        def handler(request):
            nonlocal call_count
            call_count += 1
            return json_response({"message": "service unavailable"}, status=503)

        respx.get(f"{BASE}/v1/ping").mock(side_effect=handler)

        snap = SnapAPI(api_key="sk_test", max_retries=2, retry_delay=0.0)
        with pytest.raises(SnapAPIError) as exc_info:
            snap.ping()
        assert exc_info.value.status_code == 503
        assert call_count == 3  # 1 initial + 2 retries


# ── Ping ─────────────────────────────────────────────────────────────────────

class TestPing:
    @respx.mock
    def test_returns_status_ok(self):
        respx.get(f"{BASE}/v1/ping").mock(
            return_value=json_response({"status": "ok", "timestamp": 1000000})
        )
        snap = make_client()
        result = snap.ping()
        assert result["status"] == "ok"
