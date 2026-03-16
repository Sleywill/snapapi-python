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
    RateLimitError,
    SnapAPIError,
)

BASE = "https://snapapi.pics"

pytestmark = pytest.mark.asyncio


# -- Helpers ------------------------------------------------------------------

def json_response(data: dict, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json=data)


def binary_response(data: bytes = b"\x89PNG\r\n") -> httpx.Response:
    return httpx.Response(200, content=data, headers={"Content-Type": "image/png"})


# -- Constructor ---------------------------------------------------------------

class TestAsyncConstructor:
    def test_raises_without_api_key(self):
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
