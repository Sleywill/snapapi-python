"""
Unit tests for SnapAPI Python SDK -- async client.
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
    AsyncSnapAPI,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    SnapAPIError,
)

BASE = "https://api.snapapi.pics"


# -- Helpers ------------------------------------------------------------------

def json_response(data: dict, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json=data)


def binary_response(data: bytes = b"\x89PNG\r\n") -> httpx.Response:
    return httpx.Response(200, content=data, headers={"Content-Type": "image/png"})


# -- Constructor ---------------------------------------------------------------

class TestAsyncConstructor:
    def test_raises_without_api_key(self):  # noqa: not async, no asyncio mark needed
        with pytest.raises(ValueError):
            AsyncSnapAPI(api_key="")

    async def test_context_manager(self):
        async with AsyncSnapAPI(api_key="sk_test") as snap:
            assert snap is not None


# -- screenshot() --------------------------------------------------------------

class TestAsyncScreenshot:
    async def test_raises_without_input(self):
        snap = AsyncSnapAPI(api_key="sk_test", max_retries=0)
        with pytest.raises(ValueError):
            await snap.screenshot()
        await snap.close()

    @respx.mock
    async def test_returns_bytes_for_binary_response(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.screenshot(url="https://example.com")
        assert isinstance(result, bytes)

    @respx.mock
    async def test_sends_both_auth_headers(self):
        route = respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        async with AsyncSnapAPI(api_key="sk_async_key", max_retries=0) as snap:
            await snap.screenshot(url="https://example.com")
        request = route.calls.last.request
        assert request.headers["Authorization"] == "Bearer sk_async_key"
        assert request.headers["X-Api-Key"] == "sk_async_key"


# -- screenshot_to_file() -----------------------------------------------------

class TestAsyncScreenshotToFile:
    @respx.mock
    async def test_saves_to_file(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response(b"\x89PNG_ASYNC"))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                filepath = f.name
            try:
                result = await snap.screenshot_to_file("https://example.com", filepath)
                assert result == b"\x89PNG_ASYNC"
                with open(filepath, "rb") as f:
                    assert f.read() == b"\x89PNG_ASYNC"
            finally:
                os.unlink(filepath)


# -- scrape() ------------------------------------------------------------------

class TestAsyncScrape:
    @respx.mock
    async def test_returns_scrape_result(self):
        payload = {
            "success": True,
            "results": [{"page": 1, "url": "https://example.com", "data": "async content"}],
        }
        respx.post(f"{BASE}/v1/scrape").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.scrape(url="https://example.com")
        assert result.results[0].data == "async content"


# -- extract() -----------------------------------------------------------------

class TestAsyncExtract:
    @respx.mock
    async def test_returns_extract_result(self):
        payload = {
            "success": True,
            "type": "text",
            "url": "https://example.com",
            "content": "Plain text content",
            "took": 900,
            "cached": False,
        }
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.extract(url="https://example.com", type="text")
        assert result.content == "Plain text content"


# -- video() -------------------------------------------------------------------

class TestAsyncVideo:
    @respx.mock
    async def test_returns_bytes(self):
        respx.post(f"{BASE}/v1/video").mock(
            return_value=httpx.Response(200, content=b"\x00\x00VIDEO")
        )
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.video(url="https://example.com", duration=3)
        assert isinstance(result, bytes)


# -- og_image() ----------------------------------------------------------------

class TestAsyncOgImage:
    @respx.mock
    async def test_returns_bytes(self):
        respx.post(f"{BASE}/v1/screenshot").mock(return_value=binary_response())
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.og_image(url="https://example.com")
        assert isinstance(result, bytes)


# -- analyze() -----------------------------------------------------------------

class TestAsyncAnalyze:
    @respx.mock
    async def test_returns_analyze_result(self):
        payload = {
            "success": True,
            "result": "Summary here.",
            "url": "https://example.com",
            "model": "gpt-4o",
            "provider": "openai",
            "took": 2000,
        }
        respx.post(f"{BASE}/v1/analyze").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.analyze(
                url="https://example.com",
                prompt="Summarize.",
                provider="openai",
                api_key="sk-test",
            )
        assert result.success is True
        assert result.result == "Summary here."


# -- get_usage() / quota() ----------------------------------------------------

class TestAsyncGetUsage:
    @respx.mock
    async def test_returns_usage_result(self):
        payload = {"used": 10, "limit": 500, "remaining": 490, "resetAt": "2026-04-01T00:00:00Z"}
        respx.get(f"{BASE}/v1/usage").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            usage = await snap.get_usage()
        assert usage.used == 10

    @respx.mock
    async def test_quota_is_alias(self):
        payload = {"used": 3, "limit": 100, "remaining": 97, "resetAt": ""}
        respx.get(f"{BASE}/v1/usage").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            usage = await snap.quota()
        assert usage.used == 3


# -- Error handling ------------------------------------------------------------

class TestAsyncErrorHandling:
    @respx.mock
    async def test_raises_authentication_error_on_401(self):
        respx.get(f"{BASE}/v1/ping").mock(
            return_value=json_response({"message": "Unauthorized"}, status=401)
        )
        async with AsyncSnapAPI(api_key="bad_key", max_retries=0) as snap:
            with pytest.raises(AuthenticationError):
                await snap.ping()

    @respx.mock
    async def test_raises_rate_limit_error_on_429(self):
        respx.get(f"{BASE}/v1/ping").mock(
            return_value=httpx.Response(
                429,
                json={"message": "Rate limited"},
                headers={"Retry-After": "10"},
            )
        )
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            with pytest.raises(RateLimitError) as exc_info:
                await snap.ping()
        assert exc_info.value.retry_after == 10.0


# -- Retry logic ---------------------------------------------------------------

class TestAsyncRetryLogic:
    @respx.mock
    async def test_retries_on_503_and_succeeds(self):
        call_count = 0

        def handler(request):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return json_response({"message": "unavailable"}, status=503)
            return json_response({"status": "ok", "timestamp": 999})

        respx.get(f"{BASE}/v1/ping").mock(side_effect=handler)

        async with AsyncSnapAPI(api_key="sk_test", max_retries=3, retry_delay=0.0) as snap:
            result = await snap.ping()
        assert result["status"] == "ok"
        assert call_count == 3

    @respx.mock
    async def test_does_not_retry_on_401(self):
        call_count = 0

        def handler(request):
            nonlocal call_count
            call_count += 1
            return json_response({"message": "Unauthorized"}, status=401)

        respx.get(f"{BASE}/v1/ping").mock(side_effect=handler)

        async with AsyncSnapAPI(api_key="sk_test", max_retries=3, retry_delay=0.0) as snap:
            with pytest.raises(AuthenticationError):
                await snap.ping()
        assert call_count == 1


# -- screenshot_to_storage() ---------------------------------------------------

class TestAsyncScreenshotToStorage:
    @respx.mock
    async def test_returns_dict_with_url(self):
        respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=json_response({"id": "f1", "url": "https://cdn.example.com/f1.png"})
        )
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.screenshot_to_storage("https://example.com")
        assert isinstance(result, dict)
        assert result["url"] == "https://cdn.example.com/f1.png"

    @respx.mock
    async def test_sends_storage_destination_in_payload(self):
        route = respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=json_response({"id": "f2", "url": "https://cdn.example.com/f2.png"})
        )
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            await snap.screenshot_to_storage("https://example.com", destination="user_s3")
        body = json.loads(route.calls.last.request.content)
        assert body["storage"]["destination"] == "user_s3"


# -- pdf() and pdf_to_file() ---------------------------------------------------

class TestAsyncPdf:
    async def test_raises_without_input(self):
        snap = AsyncSnapAPI(api_key="sk_test", max_retries=0)
        with pytest.raises(ValueError, match="url or html"):
            await snap.pdf()
        await snap.close()

    @respx.mock
    async def test_returns_bytes(self):
        respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=httpx.Response(200, content=b"%PDF-1.4")
        )
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.pdf(url="https://example.com")
        assert isinstance(result, bytes)
        assert result.startswith(b"%PDF")

    @respx.mock
    async def test_pdf_to_file(self):
        respx.post(f"{BASE}/v1/screenshot").mock(
            return_value=httpx.Response(200, content=b"%PDF-ASYNC")
        )
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                filepath = f.name
            try:
                result = await snap.pdf_to_file("https://example.com", filepath)
                assert result == b"%PDF-ASYNC"
                with open(filepath, "rb") as f:
                    assert f.read() == b"%PDF-ASYNC"
            finally:
                os.unlink(filepath)


# -- extract convenience methods -----------------------------------------------

class TestAsyncExtractConvenience:
    @respx.mock
    async def test_extract_markdown(self):
        payload = {"success": True, "type": "markdown", "content": "# Hello", "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.extract_markdown("https://example.com")
        body = json.loads(respx.calls.last.request.content)
        assert body["type"] == "markdown"
        assert result.content == "# Hello"

    @respx.mock
    async def test_extract_article(self):
        payload = {"success": True, "type": "article", "content": "Article body", "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.extract_article("https://example.com")
        assert result.content == "Article body"

    @respx.mock
    async def test_extract_text(self):
        payload = {"success": True, "type": "text", "content": "Plain", "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.extract_text("https://example.com")
        assert result.content == "Plain"

    @respx.mock
    async def test_extract_links(self):
        payload = {"success": True, "type": "links", "content": ["https://a.com"], "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.extract_links("https://example.com")
        assert result.content == ["https://a.com"]

    @respx.mock
    async def test_extract_images(self):
        payload = {"success": True, "type": "images", "content": ["https://img.com/a.png"], "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.extract_images("https://example.com")
        assert result.content == ["https://img.com/a.png"]

    @respx.mock
    async def test_extract_metadata(self):
        payload = {"success": True, "type": "metadata", "content": {"title": "Test"}, "url": "https://example.com"}
        respx.post(f"{BASE}/v1/extract").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.extract_metadata("https://example.com")
        assert result.content["title"] == "Test"


# -- storage_* methods ---------------------------------------------------------

class TestAsyncStorage:
    @respx.mock
    async def test_storage_list_files(self):
        payload = {
            "files": [{"id": "f1", "url": "https://cdn.example.com/f1.png"}],
            "total": 1,
        }
        respx.get(f"{BASE}/v1/storage/files?limit=50&offset=0").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.storage_list_files()
        assert len(result.files) == 1
        assert result.files[0].id == "f1"

    @respx.mock
    async def test_storage_get_file(self):
        payload = {"id": "f1", "url": "https://cdn.example.com/f1.png"}
        respx.get(f"{BASE}/v1/storage/files/f1").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.storage_get_file("f1")
        assert result.id == "f1"

    @respx.mock
    async def test_storage_delete_file(self):
        respx.delete(f"{BASE}/v1/storage/files/f1").mock(return_value=json_response({"success": True}))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.storage_delete_file("f1")
        assert result.success is True

    @respx.mock
    async def test_storage_get_usage(self):
        payload = {
            "used": 512,
            "limit": 1073741824,
            "percentage": 0.00005,
            "usedFormatted": "512 B",
            "limitFormatted": "1 GB",
        }
        respx.get(f"{BASE}/v1/storage/usage").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.storage_get_usage()
        assert result.used == 512

    @respx.mock
    async def test_storage_configure_s3(self):
        from snapapi import S3Config
        respx.post(f"{BASE}/v1/storage/s3").mock(return_value=json_response({"success": True}))
        config = S3Config(
            s3_bucket="my-bucket",
            s3_region="us-east-1",
            s3_access_key_id="AKID",
            s3_secret_access_key="secret",
        )
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.storage_configure_s3(config)
        assert result["success"] is True

    @respx.mock
    async def test_storage_test_s3(self):
        respx.post(f"{BASE}/v1/storage/s3/test").mock(
            return_value=json_response({"success": True, "message": "OK"})
        )
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.storage_test_s3()
        assert result.success is True


# -- scheduled_* methods -------------------------------------------------------

class TestAsyncScheduled:
    @respx.mock
    async def test_scheduled_create(self):
        from snapapi import CreateScheduledOptions
        payload = {
            "id": "sched_1",
            "url": "https://example.com",
            "cronExpression": "0 9 * * *",
        }
        respx.post(f"{BASE}/v1/scheduled").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.scheduled_create(
                CreateScheduledOptions(url="https://example.com", cron_expression="0 9 * * *")
            )
        assert result.id == "sched_1"

    @respx.mock
    async def test_scheduled_list(self):
        payload = {
            "jobs": [{"id": "sched_1", "url": "https://example.com", "cronExpression": "0 9 * * *"}]
        }
        respx.get(f"{BASE}/v1/scheduled").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            jobs = await snap.scheduled_list()
        assert jobs[0].id == "sched_1"

    @respx.mock
    async def test_scheduled_delete(self):
        respx.delete(f"{BASE}/v1/scheduled/sched_1").mock(return_value=json_response({"success": True}))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.scheduled_delete("sched_1")
        assert result.success is True


# -- webhooks_* methods --------------------------------------------------------

class TestAsyncWebhooks:
    @respx.mock
    async def test_webhooks_create(self):
        from snapapi import CreateWebhookOptions
        payload = {"id": "wh_1", "url": "https://my-app.com/hooks/snap", "events": ["screenshot.done"]}
        respx.post(f"{BASE}/v1/webhooks").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.webhooks_create(
                CreateWebhookOptions(url="https://my-app.com/hooks/snap", events=["screenshot.done"])
            )
        assert result.id == "wh_1"

    @respx.mock
    async def test_webhooks_list(self):
        payload = {
            "webhooks": [{"id": "wh_1", "url": "https://my-app.com/hooks/snap", "events": ["screenshot.done"]}]
        }
        respx.get(f"{BASE}/v1/webhooks").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            webhooks = await snap.webhooks_list()
        assert webhooks[0].id == "wh_1"

    @respx.mock
    async def test_webhooks_delete(self):
        respx.delete(f"{BASE}/v1/webhooks/wh_1").mock(return_value=json_response({"success": True}))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.webhooks_delete("wh_1")
        assert result.success is True


# -- keys_* methods ------------------------------------------------------------

class TestAsyncKeys:
    @respx.mock
    async def test_keys_create(self):
        payload = {"id": "key_1", "name": "production", "key": "sk_live_abc123"}
        respx.post(f"{BASE}/v1/keys").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.keys_create("production")
        assert result.key == "sk_live_abc123"

    @respx.mock
    async def test_keys_list(self):
        payload = {"keys": [{"id": "key_1", "name": "production", "key": "sk_live_***"}]}
        respx.get(f"{BASE}/v1/keys").mock(return_value=json_response(payload))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            keys = await snap.keys_list()
        assert keys[0].name == "production"

    @respx.mock
    async def test_keys_delete(self):
        respx.delete(f"{BASE}/v1/keys/key_1").mock(return_value=json_response({"success": True}))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            result = await snap.keys_delete("key_1")
        assert result.success is True


# -- Async network / timeout errors --------------------------------------------

class TestAsyncNetworkErrors:
    @respx.mock
    async def test_raises_network_error_on_connection_failure(self):
        respx.get(f"{BASE}/v1/ping").mock(side_effect=httpx.ConnectError("Connection refused"))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            with pytest.raises(NetworkError) as exc_info:
                await snap.ping()
        assert exc_info.value.code == "NETWORK_ERROR"

    @respx.mock
    async def test_raises_timeout_error_on_timeout(self):
        from snapapi import TimeoutError as SnapTimeoutError
        respx.get(f"{BASE}/v1/ping").mock(side_effect=httpx.TimeoutException("Timed out"))
        async with AsyncSnapAPI(api_key="sk_test", max_retries=0) as snap:
            with pytest.raises(SnapTimeoutError) as exc_info:
                await snap.ping()
        assert exc_info.value.code == "TIMEOUT"
