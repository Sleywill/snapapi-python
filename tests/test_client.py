"""
Unit tests for SnapAPI Python SDK -- sync client.
HTTP calls are fully mocked via respx (httpx interceptor).
"""

from __future__ import annotations

import json
import os
import tempfile

import httpx
import pytest
import respx

from snapapi import (
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
    SnapAPI,
    SnapAPIError,
    ValidationError,
    TimeoutError as SnapTimeoutError,
    NetworkError,
)

BASE = "https://api.snapapi.pics"


# -- Helpers ------------------------------------------------------------------

def make_client(**kwargs) -> SnapAPI:
    return SnapAPI(api_key="sk_test_1234", max_retries=0, **kwargs)


def json_response(data: dict, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json=data)


def binary_response(data: bytes = b"\x89PNG\r\n") -> httpx.Response:
    return httpx.Response(200, content=data, headers={"Content-Type": "image/png"})


# -- Constructor ---------------------------------------------------------------

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


# -- screenshot() --------------------------------------------------------------

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
    def test_sends_both_auth_headers(self):
        route = respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        snap = make_client()
        snap.screenshot(url="https://example.com")
        request = route.calls.last.request
        assert request.headers["Authorization"] == "Bearer sk_test_1234"
        assert request.headers["X-Api-Key"] == "sk_test_1234"

    @respx.mock
    def test_accepts_html_input(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        snap = make_client()
        result = snap.screenshot(html="<h1>Hello</h1>")
        assert isinstance(result, bytes)

    @respx.mock
    def test_accepts_markdown_input(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        snap = make_client()
        result = snap.screenshot(markdown="# Hello")
        assert isinstance(result, bytes)


# -- screenshot_to_file() -----------------------------------------------------

class TestScreenshotToFile:
    @respx.mock
    def test_saves_to_file_and_returns_bytes(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response(b"\x89PNG_TEST"))
        snap = make_client()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            filepath = f.name
        try:
            result = snap.screenshot_to_file("https://example.com", filepath)
            assert isinstance(result, bytes)
            assert result == b"\x89PNG_TEST"
            with open(filepath, "rb") as f:
                assert f.read() == b"\x89PNG_TEST"
        finally:
            os.unlink(filepath)

    @respx.mock
    def test_passes_additional_options(self):
        route = respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        snap = make_client()
        with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as f:
            filepath = f.name
        try:
            snap.screenshot_to_file(
                "https://example.com", filepath,
                format="webp", full_page=True, dark_mode=True,
            )
            request = route.calls.last.request
            body = json.loads(request.content)
            assert body["format"] == "webp"
            assert body["fullPage"] is True
            assert body["darkMode"] is True
        finally:
            os.unlink(filepath)


# -- pdf() ---------------------------------------------------------------------

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

    @respx.mock
    def test_accepts_html(self):
        respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=httpx.Response(200, content=b"%PDF-1.4")
        )
        snap = make_client()
        result = snap.pdf(html="<h1>Invoice</h1>")
        assert isinstance(result, bytes)


# -- pdf_to_file() ------------------------------------------------------------

class TestPdfToFile:
    @respx.mock
    def test_saves_to_file(self):
        respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=httpx.Response(200, content=b"%PDF-1.4-TEST")
        )
        snap = make_client()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            filepath = f.name
        try:
            result = snap.pdf_to_file("https://example.com", filepath)
            assert result == b"%PDF-1.4-TEST"
            with open(filepath, "rb") as f:
                assert f.read() == b"%PDF-1.4-TEST"
        finally:
            os.unlink(filepath)


# -- scrape() ------------------------------------------------------------------

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


# -- extract() -----------------------------------------------------------------

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


# -- video() -------------------------------------------------------------------

class TestVideo:
    @respx.mock
    def test_returns_bytes(self):
        respx.post(f"{BASE}/v1/video").mock(
            return_value=httpx.Response(200, content=b"\x00\x00VIDEO", headers={"Content-Type": "video/mp4"})
        )
        snap = make_client()
        result = snap.video(url="https://example.com", duration=3)
        assert isinstance(result, bytes)


# -- og_image() ----------------------------------------------------------------

class TestOgImage:
    @respx.mock
    def test_returns_bytes(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        snap = make_client()
        result = snap.og_image(url="https://example.com")
        assert isinstance(result, bytes)


# -- analyze() -----------------------------------------------------------------

class TestAnalyze:
    @respx.mock
    def test_returns_analyze_result(self):
        payload = {
            "success": True,
            "result": "This page is about testing.",
            "url": "https://example.com",
            "model": "gpt-4o",
            "provider": "openai",
            "took": 3500,
        }
        respx.post(f"{BASE}/v1/analyze").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.analyze(
            url="https://example.com",
            prompt="Summarize this page.",
            provider="openai",
            api_key="sk-test",
        )
        assert result.success is True
        assert result.result == "This page is about testing."


# -- get_usage() / quota() ----------------------------------------------------

class TestGetUsage:
    @respx.mock
    def test_returns_usage_result(self):
        payload = {"used": 42, "limit": 1000, "remaining": 958, "resetAt": "2026-04-01T00:00:00Z"}
        respx.get(f"{BASE}/v1/usage").mock(return_value=json_response(payload))
        snap = make_client()
        usage = snap.get_usage()
        assert usage.used == 42
        assert usage.remaining == 958

    @respx.mock
    def test_quota_is_alias_for_get_usage(self):
        payload = {"used": 5, "limit": 500, "remaining": 495, "resetAt": ""}
        respx.get(f"{BASE}/v1/usage").mock(return_value=json_response(payload))
        snap = make_client()
        usage = snap.quota()
        assert usage.used == 5


# -- ping() -------------------------------------------------------------------

class TestPing:
    @respx.mock
    def test_returns_status_ok(self):
        respx.get(f"{BASE}/v1/ping").mock(
            return_value=json_response({"status": "ok", "timestamp": 1000000})
        )
        snap = make_client()
        result = snap.ping()
        assert result["status"] == "ok"


# -- Error handling ------------------------------------------------------------

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
    def test_raises_authentication_error_on_403(self):
        respx.get(f"{BASE}/v1/ping").mock(
            return_value=json_response({"message": "Forbidden"}, status=403)
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


# -- Retry logic ---------------------------------------------------------------

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

    @respx.mock
    def test_does_not_retry_on_401(self):
        call_count = 0

        def handler(request):
            nonlocal call_count
            call_count += 1
            return json_response({"message": "Unauthorized"}, status=401)

        respx.get(f"{BASE}/v1/ping").mock(side_effect=handler)

        snap = SnapAPI(api_key="sk_test", max_retries=3, retry_delay=0.0)
        with pytest.raises(AuthenticationError):
            snap.ping()
        assert call_count == 1

    @respx.mock
    def test_does_not_retry_on_422(self):
        call_count = 0

        def handler(request):
            nonlocal call_count
            call_count += 1
            return json_response({"message": "Bad input", "error": "VALIDATION_ERROR"}, status=422)

        respx.post(f"{BASE}/v1/screenshot").mock(side_effect=handler)

        snap = SnapAPI(api_key="sk_test", max_retries=3, retry_delay=0.0)
        with pytest.raises(ValidationError):
            snap.screenshot(url="bad")
        assert call_count == 1


# -- Error class structure -----------------------------------------------------

class TestErrorClassStructure:
    def test_snap_api_error_attributes(self):
        err = SnapAPIError("test", "TEST_CODE", 418)
        assert err.code == "TEST_CODE"
        assert err.status_code == 418
        assert str(err) == "[TEST_CODE] test"
        assert isinstance(err, Exception)

    def test_rate_limit_error_has_retry_after(self):
        err = RateLimitError("too fast", retry_after=10.0)
        assert err.retry_after == 10.0
        assert err.status_code == 429
        assert isinstance(err, SnapAPIError)

    def test_authentication_error_inherits(self):
        err = AuthenticationError("bad key")
        assert isinstance(err, SnapAPIError)
        assert err.status_code == 401

    def test_validation_error_has_fields(self):
        err = ValidationError("bad", fields={"url": "invalid"})
        assert err.fields["url"] == "invalid"
        assert err.status_code == 422

    def test_quota_exceeded_error_status(self):
        err = QuotaExceededError("exceeded")
        assert err.status_code == 402

    def test_timeout_error_status(self):
        err = SnapTimeoutError()
        assert err.status_code == 0
        assert err.code == "TIMEOUT"

    def test_network_error_status(self):
        err = NetworkError("connection refused")
        assert err.status_code == 0
        assert err.code == "NETWORK_ERROR"


# -- screenshot_to_storage() ---------------------------------------------------

class TestScreenshotToStorage:
    @respx.mock
    def test_returns_dict_with_url(self):
        respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=json_response({"id": "f1", "url": "https://cdn.example.com/f1.png"})
        )
        snap = make_client()
        result = snap.screenshot_to_storage("https://example.com")
        assert isinstance(result, dict)
        assert result["url"] == "https://cdn.example.com/f1.png"

    @respx.mock
    def test_sends_storage_destination_in_payload(self):
        route = respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=json_response({"id": "f2", "url": "https://cdn.example.com/f2.png"})
        )
        snap = make_client()
        snap.screenshot_to_storage("https://example.com", destination="user_s3")
        body = json.loads(route.calls.last.request.content)
        assert body["storage"]["destination"] == "user_s3"


# -- extract convenience methods -----------------------------------------------

class TestExtractConvenience:
    @respx.mock
    def test_extract_markdown(self):
        payload = {"success": True, "type": "markdown", "content": "# Hello", "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.extract_markdown("https://example.com")
        body = json.loads(respx.calls.last.request.content)
        assert body["type"] == "markdown"
        assert result.content == "# Hello"

    @respx.mock
    def test_extract_article(self):
        payload = {"success": True, "type": "article", "content": "Article body", "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.extract_article("https://example.com")
        body = json.loads(respx.calls.last.request.content)
        assert body["type"] == "article"
        assert result.content == "Article body"

    @respx.mock
    def test_extract_text(self):
        payload = {"success": True, "type": "text", "content": "Plain text", "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.extract_text("https://example.com")
        body = json.loads(respx.calls.last.request.content)
        assert body["type"] == "text"
        assert result.content == "Plain text"

    @respx.mock
    def test_extract_links(self):
        payload = {"success": True, "type": "links", "content": ["https://a.com"], "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.extract_links("https://example.com")
        body = json.loads(respx.calls.last.request.content)
        assert body["type"] == "links"
        assert result.content == ["https://a.com"]

    @respx.mock
    def test_extract_images(self):
        payload = {"success": True, "type": "images", "content": ["https://img.com/a.png"], "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.extract_images("https://example.com")
        body = json.loads(respx.calls.last.request.content)
        assert body["type"] == "images"

    @respx.mock
    def test_extract_metadata(self):
        payload = {"success": True, "type": "metadata", "content": {"title": "Test"}, "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.extract_metadata("https://example.com")
        body = json.loads(respx.calls.last.request.content)
        assert body["type"] == "metadata"
        assert result.content["title"] == "Test"


# -- storage_* methods ---------------------------------------------------------

class TestStorage:
    @respx.mock
    def test_storage_list_files(self):
        payload = {
            "files": [{"id": "f1", "url": "https://cdn.example.com/f1.png"}],
            "total": 1,
        }
        respx.get(f"{BASE}/v1/storage/files?limit=50&offset=0").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.storage_list_files()
        assert len(result.files) == 1
        assert result.files[0].id == "f1"

    @respx.mock
    def test_storage_get_file(self):
        payload = {"id": "f1", "url": "https://cdn.example.com/f1.png", "filename": "f1.png"}
        respx.get(f"{BASE}/v1/storage/files/f1").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.storage_get_file("f1")
        assert result.id == "f1"
        assert result.filename == "f1.png"

    @respx.mock
    def test_storage_delete_file(self):
        respx.delete(f"{BASE}/v1/storage/files/f1").mock(return_value=json_response({"success": True}))
        snap = make_client()
        result = snap.storage_delete_file("f1")
        assert result.success is True

    @respx.mock
    def test_storage_get_usage(self):
        payload = {
            "used": 1024,
            "limit": 1073741824,
            "percentage": 0.0001,
            "usedFormatted": "1 KB",
            "limitFormatted": "1 GB",
        }
        respx.get(f"{BASE}/v1/storage/usage").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.storage_get_usage()
        assert result.used == 1024

    @respx.mock
    def test_storage_configure_s3(self):
        from snapapi import S3Config
        respx.post(f"{BASE}/v1/storage/s3").mock(return_value=json_response({"success": True}))
        snap = make_client()
        config = S3Config(
            s3_bucket="my-bucket",
            s3_region="us-east-1",
            s3_access_key_id="AKID",
            s3_secret_access_key="secret",
        )
        result = snap.storage_configure_s3(config)
        assert result["success"] is True

    @respx.mock
    def test_storage_test_s3(self):
        respx.post(f"{BASE}/v1/storage/s3/test").mock(
            return_value=json_response({"success": True, "message": "Connection OK"})
        )
        snap = make_client()
        result = snap.storage_test_s3()
        assert result.success is True
        assert result.message == "Connection OK"


# -- scheduled_* methods -------------------------------------------------------

class TestScheduled:
    @respx.mock
    def test_scheduled_create(self):
        from snapapi import CreateScheduledOptions
        payload = {
            "id": "sched_1",
            "url": "https://example.com",
            "cronExpression": "0 9 * * *",
            "nextRun": "2026-04-01T09:00:00Z",
        }
        respx.post(f"{BASE}/v1/scheduled").mock(return_value=json_response(payload))
        snap = make_client()
        options = CreateScheduledOptions(
            url="https://example.com",
            cron_expression="0 9 * * *",
        )
        result = snap.scheduled_create(options)
        assert result.id == "sched_1"
        assert result.cron_expression == "0 9 * * *"

    @respx.mock
    def test_scheduled_list(self):
        payload = {
            "jobs": [
                {"id": "sched_1", "url": "https://example.com", "cronExpression": "0 9 * * *"},
            ]
        }
        respx.get(f"{BASE}/v1/scheduled").mock(return_value=json_response(payload))
        snap = make_client()
        jobs = snap.scheduled_list()
        assert len(jobs) == 1
        assert jobs[0].id == "sched_1"

    @respx.mock
    def test_scheduled_list_returns_list_directly(self):
        payload = [
            {"id": "sched_2", "url": "https://example.com", "cronExpression": "0 10 * * *"},
        ]
        respx.get(f"{BASE}/v1/scheduled").mock(return_value=json_response(payload))
        snap = make_client()
        jobs = snap.scheduled_list()
        assert jobs[0].id == "sched_2"

    @respx.mock
    def test_scheduled_delete(self):
        respx.delete(f"{BASE}/v1/scheduled/sched_1").mock(return_value=json_response({"success": True}))
        snap = make_client()
        result = snap.scheduled_delete("sched_1")
        assert result.success is True


# -- webhooks_* methods --------------------------------------------------------

class TestWebhooks:
    @respx.mock
    def test_webhooks_create(self):
        from snapapi import CreateWebhookOptions
        payload = {
            "id": "wh_1",
            "url": "https://my-app.com/hooks/snap",
            "events": ["screenshot.done"],
        }
        respx.post(f"{BASE}/v1/webhooks").mock(return_value=json_response(payload))
        snap = make_client()
        options = CreateWebhookOptions(
            url="https://my-app.com/hooks/snap",
            events=["screenshot.done"],
            secret="mysecret",
        )
        result = snap.webhooks_create(options)
        assert result.id == "wh_1"
        assert result.events == ["screenshot.done"]

    @respx.mock
    def test_webhooks_list(self):
        payload = {
            "webhooks": [
                {"id": "wh_1", "url": "https://my-app.com/hooks/snap", "events": ["screenshot.done"]},
            ]
        }
        respx.get(f"{BASE}/v1/webhooks").mock(return_value=json_response(payload))
        snap = make_client()
        webhooks = snap.webhooks_list()
        assert len(webhooks) == 1
        assert webhooks[0].id == "wh_1"

    @respx.mock
    def test_webhooks_list_returns_list_directly(self):
        payload = [
            {"id": "wh_2", "url": "https://my-app.com/hooks/snap2", "events": ["pdf.done"]},
        ]
        respx.get(f"{BASE}/v1/webhooks").mock(return_value=json_response(payload))
        snap = make_client()
        webhooks = snap.webhooks_list()
        assert webhooks[0].id == "wh_2"

    @respx.mock
    def test_webhooks_delete(self):
        respx.delete(f"{BASE}/v1/webhooks/wh_1").mock(return_value=json_response({"success": True}))
        snap = make_client()
        result = snap.webhooks_delete("wh_1")
        assert result.success is True


# -- keys_* methods ------------------------------------------------------------

class TestKeys:
    @respx.mock
    def test_keys_create(self):
        payload = {"id": "key_1", "name": "production", "key": "sk_live_abc123"}
        respx.post(f"{BASE}/v1/keys").mock(return_value=json_response(payload))
        snap = make_client()
        result = snap.keys_create("production")
        assert result.id == "key_1"
        assert result.key == "sk_live_abc123"

    @respx.mock
    def test_keys_list(self):
        payload = {
            "keys": [
                {"id": "key_1", "name": "production", "key": "sk_live_***"},
            ]
        }
        respx.get(f"{BASE}/v1/keys").mock(return_value=json_response(payload))
        snap = make_client()
        keys = snap.keys_list()
        assert len(keys) == 1
        assert keys[0].name == "production"

    @respx.mock
    def test_keys_list_returns_list_directly(self):
        payload = [
            {"id": "key_2", "name": "staging", "key": "sk_live_***"},
        ]
        respx.get(f"{BASE}/v1/keys").mock(return_value=json_response(payload))
        snap = make_client()
        keys = snap.keys_list()
        assert keys[0].id == "key_2"

    @respx.mock
    def test_keys_delete(self):
        respx.delete(f"{BASE}/v1/keys/key_1").mock(return_value=json_response({"success": True}))
        snap = make_client()
        result = snap.keys_delete("key_1")
        assert result.success is True


# -- Network and timeout errors ------------------------------------------------

class TestNetworkErrors:
    @respx.mock
    def test_raises_network_error_on_connection_failure(self):
        respx.get(f"{BASE}/v1/ping").mock(side_effect=httpx.ConnectError("Connection refused"))
        snap = make_client()
        with pytest.raises(NetworkError) as exc_info:
            snap.ping()
        assert exc_info.value.code == "NETWORK_ERROR"

    @respx.mock
    def test_raises_timeout_error_on_timeout(self):
        respx.get(f"{BASE}/v1/ping").mock(side_effect=httpx.TimeoutException("Timed out"))
        snap = make_client()
        with pytest.raises(SnapTimeoutError) as exc_info:
            snap.ping()
        assert exc_info.value.code == "TIMEOUT"

    @respx.mock
    def test_error_repr_contains_class_name(self):
        err = SnapAPIError("test message", "TEST_CODE", 418)
        assert "SnapAPIError" in repr(err)
        assert "418" in repr(err)


# -- generate_pdf() alias -----------------------------------------------------

class TestGeneratePdf:
    @respx.mock
    def test_returns_bytes(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response(b"%PDF-1.4"))
        snap = make_client()
        result = snap.generate_pdf(url="https://example.com")
        assert isinstance(result, bytes)
        assert result.startswith(b"%PDF")

    def test_raises_without_input(self):
        snap = make_client()
        with pytest.raises(ValueError, match="url or html"):
            snap.generate_pdf()


# -- generate_og_image() alias ------------------------------------------------

class TestGenerateOgImage:
    @respx.mock
    def test_returns_bytes(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        snap = make_client()
        result = snap.generate_og_image(url="https://example.com")
        assert isinstance(result, bytes)


# -- Retry logic tests --------------------------------------------------------

class TestRetryLogic:
    @respx.mock
    def test_retries_on_429_and_succeeds(self):
        route = respx.get(f"{BASE}/v1/ping")
        route.side_effect = [
            httpx.Response(429, json={"message": "Too many requests"}, headers={"Retry-After": "0"}),
            httpx.Response(200, json={"status": "ok", "timestamp": 123}),
        ]
        snap = SnapAPI(api_key="sk_test", max_retries=2, retry_delay=0.001)
        result = snap.ping()
        assert result["status"] == "ok"
        assert route.call_count == 2

    @respx.mock
    def test_retries_on_500_and_succeeds(self):
        route = respx.get(f"{BASE}/v1/ping")
        route.side_effect = [
            httpx.Response(500, json={"message": "Internal error"}),
            httpx.Response(200, json={"status": "ok", "timestamp": 123}),
        ]
        snap = SnapAPI(api_key="sk_test", max_retries=2, retry_delay=0.001)
        result = snap.ping()
        assert result["status"] == "ok"
        assert route.call_count == 2

    @respx.mock
    def test_does_not_retry_on_401(self):
        route = respx.get(f"{BASE}/v1/ping")
        route.mock(return_value=httpx.Response(401, json={"message": "Unauthorized"}))
        snap = SnapAPI(api_key="sk_bad", max_retries=3, retry_delay=0.001)
        with pytest.raises(AuthenticationError):
            snap.ping()
        assert route.call_count == 1

    @respx.mock
    def test_does_not_retry_on_422(self):
        route = respx.post(f"{BASE}/v1/screenshot")
        route.mock(return_value=httpx.Response(
            422, json={"message": "Validation failed", "fields": {"url": "required"}}
        ))
        snap = SnapAPI(api_key="sk_test", max_retries=3, retry_delay=0.001)
        with pytest.raises(ValidationError):
            snap.screenshot(url="https://example.com")
        assert route.call_count == 1

    @respx.mock
    def test_exhausts_retries_and_raises(self):
        route = respx.get(f"{BASE}/v1/ping")
        route.mock(return_value=httpx.Response(500, json={"message": "Server error"}))
        snap = SnapAPI(api_key="sk_test", max_retries=2, retry_delay=0.001)
        with pytest.raises(SnapAPIError):
            snap.ping()
        assert route.call_count == 3  # initial + 2 retries

    @respx.mock
    def test_retries_network_error_and_succeeds(self):
        route = respx.get(f"{BASE}/v1/ping")
        route.side_effect = [
            httpx.ConnectError("Connection refused"),
            httpx.Response(200, json={"status": "ok", "timestamp": 123}),
        ]
        snap = SnapAPI(api_key="sk_test", max_retries=2, retry_delay=0.001)
        result = snap.ping()
        assert result["status"] == "ok"
        assert route.call_count == 2

    @respx.mock
    def test_retries_timeout_error_and_succeeds(self):
        route = respx.get(f"{BASE}/v1/ping")
        route.side_effect = [
            httpx.TimeoutException("Timed out"),
            httpx.Response(200, json={"status": "ok", "timestamp": 123}),
        ]
        snap = SnapAPI(api_key="sk_test", max_retries=2, retry_delay=0.001)
        result = snap.ping()
        assert result["status"] == "ok"
        assert route.call_count == 2

    @respx.mock
    def test_exhausts_timeout_retries_and_raises(self):
        route = respx.get(f"{BASE}/v1/ping")
        route.mock(side_effect=httpx.TimeoutException("Timed out"))
        snap = SnapAPI(api_key="sk_test", max_retries=1, retry_delay=0.001)
        with pytest.raises(SnapTimeoutError):
            snap.ping()
        assert route.call_count == 2  # initial + 1 retry
