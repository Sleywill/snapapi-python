"""
SnapAPI Async Python Client (aiohttp-based)

Usage::

    import asyncio
    from snapapi import AsyncSnapAPI

    async def main():
        client = AsyncSnapAPI(api_key="sk_live_YOUR_KEY")
        buf = await client.screenshot(url="https://example.com")
        with open("shot.png", "wb") as f:
            f.write(buf)

    asyncio.run(main())

Requires: pip install aiohttp
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

try:
    import aiohttp
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "aiohttp is required for AsyncSnapAPI: pip install aiohttp"
    ) from exc

from .client import SnapAPIError
from .types import (
    ScreenshotOptions,
    ScreenshotResult,
    ExtractOptions,
    ExtractResult,
    ScrapeOptions,
    ScrapeResult,
    AnalyzeOptions,
    AnalyzeResult,
    Cookie,
    HttpAuth,
    ProxyConfig,
    Geolocation,
    PdfOptions,
    ThumbnailOptions,
    ExtractMetadata,
    DevicePreset,
    StorageFile,
    StorageListResult,
    StorageUsage,
    S3Config,
    S3TestResult,
    DeleteResult,
    CreateScheduledOptions,
    ScheduledScreenshot,
    CreateWebhookOptions,
    Webhook,
    ApiKey,
    CreateApiKeyResult,
)


class AsyncSnapAPI:
    """
    Async SnapAPI client (powered by aiohttp).

    Example::

        async with AsyncSnapAPI(api_key="sk_live_xxx") as client:
            buf = await client.screenshot(url="https://example.com")
    """

    DEFAULT_BASE_URL = "https://api.snapapi.pics"
    DEFAULT_TIMEOUT = 60

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout or self.DEFAULT_TIMEOUT)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "AsyncSnapAPI":
        self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    def _headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "snapapi-python/2.0.0",
        }

    async def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode() if data is not None else None
        session = self._get_session()

        async with session.request(method, url, data=body, headers=self._headers()) as resp:
            raw = await resp.read()
            if resp.status >= 400:
                try:
                    body_json = json.loads(raw)
                    message = body_json.get("message", f"HTTP {resp.status}")
                    code = body_json.get("error", "HTTP_ERROR")
                    if isinstance(code, str):
                        code = code.replace(" ", "_").upper()
                    else:
                        code = "HTTP_ERROR"
                except Exception:
                    message = f"HTTP {resp.status}"
                    code = "HTTP_ERROR"
                raise SnapAPIError(message=message, code=code, status_code=resp.status)
            return raw

    # ── Screenshot ──────────────────────────────────────────────────────────

    async def screenshot(
        self,
        url: Optional[str] = None,
        html: Optional[str] = None,
        markdown: Optional[str] = None,
        format: str = "png",
        quality: Optional[int] = None,
        device: Optional[DevicePreset] = None,
        width: int = 1280,
        height: int = 800,
        full_page: bool = False,
        selector: Optional[str] = None,
        delay: int = 0,
        timeout: int = 30000,
        wait_until: Optional[str] = None,
        wait_for_selector: Optional[str] = None,
        dark_mode: bool = False,
        reduced_motion: bool = False,
        css: Optional[str] = None,
        javascript: Optional[str] = None,
        hide_selectors: Optional[List[str]] = None,
        click_selector: Optional[str] = None,
        block_ads: bool = False,
        block_trackers: bool = False,
        block_cookie_banners: bool = False,
        block_chat_widgets: bool = False,
        user_agent: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        cookies: Optional[List[Cookie]] = None,
        http_auth: Optional[HttpAuth] = None,
        proxy: Optional[ProxyConfig] = None,
        premium_proxy: Optional[bool] = None,
        geolocation: Optional[Geolocation] = None,
        timezone: Optional[str] = None,
        pdf_options: Optional[PdfOptions] = None,
        storage: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
        job_id: Optional[str] = None,
        full_page_scroll_delay: Optional[int] = None,
        full_page_max_height: Optional[int] = None,
        response_type: str = "binary",
        include_metadata: bool = False,
        device_scale_factor: float = 1.0,
        is_mobile: bool = False,
        has_touch: bool = False,
        page_size: Optional[str] = None,
        landscape: Optional[bool] = None,
        margins: Optional[Dict[str, str]] = None,
    ) -> Union[bytes, Dict[str, Any]]:
        """
        Capture a screenshot asynchronously.

        Returns bytes for binary/image, or dict for storage/async responses.
        """
        if not url and not html and not markdown:
            raise ValueError("One of url, html, or markdown is required")

        payload: Dict[str, Any] = {"format": format}
        if url:
            payload["url"] = url
        if html:
            payload["html"] = html
        if markdown:
            payload["markdown"] = markdown
        if quality is not None:
            payload["quality"] = quality
        if device:
            payload["device"] = device
        payload["width"] = width
        payload["height"] = height
        if device_scale_factor != 1.0:
            payload["deviceScaleFactor"] = device_scale_factor
        if is_mobile:
            payload["isMobile"] = True
        if has_touch:
            payload["hasTouch"] = True
        if full_page:
            payload["fullPage"] = True
        if full_page_scroll_delay is not None:
            payload["fullPageScrollDelay"] = full_page_scroll_delay
        if full_page_max_height is not None:
            payload["fullPageMaxHeight"] = full_page_max_height
        if selector:
            payload["selector"] = selector
        if delay > 0:
            payload["delay"] = delay
        if timeout != 30000:
            payload["timeout"] = timeout
        if wait_until:
            payload["waitUntil"] = wait_until
        if wait_for_selector:
            payload["waitForSelector"] = wait_for_selector
        if dark_mode:
            payload["darkMode"] = True
        if reduced_motion:
            payload["reducedMotion"] = True
        if css:
            payload["css"] = css
        if javascript:
            payload["javascript"] = javascript
        if hide_selectors:
            payload["hideSelectors"] = hide_selectors
        if click_selector:
            payload["clickSelector"] = click_selector
        if block_ads:
            payload["blockAds"] = True
        if block_trackers:
            payload["blockTrackers"] = True
        if block_cookie_banners:
            payload["blockCookieBanners"] = True
        if block_chat_widgets:
            payload["blockChatWidgets"] = True
        if user_agent:
            payload["userAgent"] = user_agent
        if extra_headers:
            payload["extraHeaders"] = extra_headers
        if cookies:
            payload["cookies"] = [c.to_dict() for c in cookies]
        if http_auth:
            payload["httpAuth"] = http_auth.to_dict()
        if proxy:
            payload["proxy"] = proxy.to_dict()
        if premium_proxy is not None:
            payload["premiumProxy"] = premium_proxy
        if geolocation:
            payload["geolocation"] = geolocation.to_dict()
        if timezone:
            payload["timezone"] = timezone
        if pdf_options:
            payload["pdfOptions"] = pdf_options.to_dict()
        if page_size:
            payload["pageSize"] = page_size
        if landscape is not None:
            payload["landscape"] = landscape
        if margins:
            payload["margins"] = margins
        if storage is not None:
            payload["storage"] = storage
        if webhook_url:
            payload["webhookUrl"] = webhook_url
        if job_id:
            payload["jobId"] = job_id
        if include_metadata:
            payload["includeMetadata"] = True
        if response_type != "binary":
            payload["responseType"] = response_type

        raw = await self._request("POST", "/v1/screenshot", payload)

        if storage is not None or webhook_url is not None or job_id is not None:
            return json.loads(raw)
        if response_type in ("json", "base64"):
            return json.loads(raw)
        return raw

    # ── Scrape ──────────────────────────────────────────────────────────────

    async def scrape(self, options: ScrapeOptions) -> ScrapeResult:
        """Scrape a page (or multiple pages) asynchronously."""
        if not options.url:
            raise ValueError("url is required")
        raw = await self._request("POST", "/v1/scrape", options.to_dict())
        return ScrapeResult.from_dict(json.loads(raw))

    # ── Extract ─────────────────────────────────────────────────────────────

    async def extract(self, options: ExtractOptions) -> ExtractResult:
        """Extract content from a webpage asynchronously."""
        if not options.url:
            raise ValueError("url is required")
        raw = await self._request("POST", "/v1/extract", options.to_dict())
        return ExtractResult.from_dict(json.loads(raw))

    # ── Analyze ─────────────────────────────────────────────────────────────

    async def analyze(self, options: AnalyzeOptions) -> AnalyzeResult:
        """Analyze a webpage with an LLM asynchronously (BYOK)."""
        if not options.url:
            raise ValueError("url is required")
        if not options.prompt:
            raise ValueError("prompt is required")
        if not options.api_key:
            raise ValueError("api_key (LLM provider key) is required")
        raw = await self._request("POST", "/v1/analyze", options.to_dict())
        return AnalyzeResult.from_dict(json.loads(raw))

    # ── Storage ─────────────────────────────────────────────────────────────

    async def storage_list_files(self, limit: int = 50, offset: int = 0) -> StorageListResult:
        """List stored files."""
        raw = await self._request("GET", f"/v1/storage/files?limit={limit}&offset={offset}")
        return StorageListResult.from_dict(json.loads(raw))

    async def storage_get_file(self, file_id: str) -> StorageFile:
        """Get a specific stored file."""
        raw = await self._request("GET", f"/v1/storage/files/{file_id}")
        return StorageFile.from_dict(json.loads(raw))

    async def storage_delete_file(self, file_id: str) -> DeleteResult:
        """Delete a stored file."""
        raw = await self._request("DELETE", f"/v1/storage/files/{file_id}")
        return DeleteResult.from_dict(json.loads(raw))

    async def storage_get_usage(self) -> StorageUsage:
        """Get storage usage for this account."""
        raw = await self._request("GET", "/v1/storage/usage")
        return StorageUsage.from_dict(json.loads(raw))

    async def storage_configure_s3(self, config: S3Config) -> Dict[str, Any]:
        """Configure a custom S3-compatible storage backend."""
        raw = await self._request("POST", "/v1/storage/s3", config.to_dict())
        return json.loads(raw)

    async def storage_test_s3(self) -> S3TestResult:
        """Test the custom S3 connection."""
        raw = await self._request("POST", "/v1/storage/s3/test", {})
        return S3TestResult.from_dict(json.loads(raw))

    # ── Scheduled ───────────────────────────────────────────────────────────

    async def scheduled_create(self, options: CreateScheduledOptions) -> ScheduledScreenshot:
        """Create a scheduled screenshot job."""
        raw = await self._request("POST", "/v1/scheduled", options.to_dict())
        return ScheduledScreenshot.from_dict(json.loads(raw))

    async def scheduled_list(self) -> List[ScheduledScreenshot]:
        """List all scheduled screenshot jobs."""
        raw = await self._request("GET", "/v1/scheduled")
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("jobs", [])
        return [ScheduledScreenshot.from_dict(j) for j in items]

    async def scheduled_delete(self, job_id: str) -> DeleteResult:
        """Delete a scheduled screenshot job."""
        raw = await self._request("DELETE", f"/v1/scheduled/{job_id}")
        return DeleteResult.from_dict(json.loads(raw))

    # ── Webhooks ────────────────────────────────────────────────────────────

    async def webhooks_create(self, options: CreateWebhookOptions) -> Webhook:
        """Register a webhook endpoint."""
        raw = await self._request("POST", "/v1/webhooks", options.to_dict())
        return Webhook.from_dict(json.loads(raw))

    async def webhooks_list(self) -> List[Webhook]:
        """List registered webhooks."""
        raw = await self._request("GET", "/v1/webhooks")
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("webhooks", [])
        return [Webhook.from_dict(w) for w in items]

    async def webhooks_delete(self, webhook_id: str) -> DeleteResult:
        """Delete a webhook."""
        raw = await self._request("DELETE", f"/v1/webhooks/{webhook_id}")
        return DeleteResult.from_dict(json.loads(raw))

    # ── API Keys ────────────────────────────────────────────────────────────

    async def keys_list(self) -> List[ApiKey]:
        """List API keys (values are masked)."""
        raw = await self._request("GET", "/v1/keys")
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("keys", [])
        return [ApiKey.from_dict(k) for k in items]

    async def keys_create(self, name: str) -> CreateApiKeyResult:
        """Create a new API key. Full key is returned only once."""
        raw = await self._request("POST", "/v1/keys", {"name": name})
        return CreateApiKeyResult.from_dict(json.loads(raw))

    async def keys_delete(self, key_id: str) -> DeleteResult:
        """Delete an API key."""
        raw = await self._request("DELETE", f"/v1/keys/{key_id}")
        return DeleteResult.from_dict(json.loads(raw))

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
