"""
Asynchronous SnapAPI client (httpx-based).

Uses ``httpx.AsyncClient`` under the hood, which supports connection
pooling, timeouts, and HTTP/2.

Example::

    import asyncio
    from snapapi import AsyncSnapAPI

    async def main():
        async with AsyncSnapAPI(api_key="sk_live_...") as snap:
            buf = await snap.screenshot(url="https://example.com")
            with open("shot.png", "wb") as f:
                f.write(buf)

    asyncio.run(main())
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import httpx
except ImportError as exc:
    raise ImportError(
        "httpx is required for AsyncSnapAPI: pip install httpx"
    ) from exc

from ._http import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    build_headers,
    compute_backoff,
    parse_error_response,
    should_retry,
)
from .exceptions import NetworkError, SnapAPIError, TimeoutError
from .types import (
    AnalyzeOptions,
    AnalyzeResult,
    ApiKey,
    Cookie,
    CreateApiKeyResult,
    CreateScheduledOptions,
    CreateWebhookOptions,
    DeleteResult,
    DevicePreset,
    ExtractOptions,
    ExtractResult,
    Geolocation,
    HttpAuth,
    ProxyConfig,
    S3Config,
    S3TestResult,
    ScheduledScreenshot,
    ScrapeOptions,
    ScrapeResult,
    ScreenshotOptions,
    StorageFile,
    StorageListResult,
    StorageUsage,
    UsageResult,
    VideoOptions,
    Webhook,
)


class AsyncSnapAPI:
    """Asynchronous SnapAPI client.

    Supports the async context-manager protocol::

        async with AsyncSnapAPI(api_key="sk_live_...") as snap:
            buf = await snap.screenshot(url="https://example.com")

    Args:
        api_key: Your SnapAPI key (required).
        base_url: Override the API base URL.
        timeout: Request timeout in seconds (default: 60).
        max_retries: Maximum automatic retries on 429 / 5xx (default: 3).
        retry_delay: Initial backoff delay in seconds (default: 0.5).
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Optional[httpx.AsyncClient] = None

    # -- Context manager ---------------------------------------------------------

    async def __aenter__(self) -> "AsyncSnapAPI":
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=build_headers(self.api_key),
        )
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=build_headers(self.api_key),
            )
        return self._client

    # -- Screenshot --------------------------------------------------------------

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
        device_scale_factor: float = 1.0,
        is_mobile: bool = False,
        has_touch: bool = False,
        full_page: bool = False,
        full_page_scroll_delay: Optional[int] = None,
        full_page_max_height: Optional[int] = None,
        selector: Optional[str] = None,
        delay: int = 0,
        timeout: Optional[int] = None,
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
        storage: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
        job_id: Optional[str] = None,
        page_size: Optional[str] = None,
        landscape: Optional[bool] = None,
        margins: Optional[Dict[str, str]] = None,
    ) -> Union[bytes, Dict[str, Any]]:
        """Capture a screenshot asynchronously.

        Args and returns are identical to :meth:`SnapAPI.screenshot`.
        """
        if not url and not html and not markdown:
            raise ValueError("One of url, html, or markdown is required")

        opts = ScreenshotOptions(
            url=url,
            html=html,
            markdown=markdown,
            format=format,  # type: ignore[arg-type]
            quality=quality,
            device=device,
            width=width,
            height=height,
            device_scale_factor=device_scale_factor,
            is_mobile=is_mobile,
            has_touch=has_touch,
            full_page=full_page,
            full_page_scroll_delay=full_page_scroll_delay,
            full_page_max_height=full_page_max_height,
            selector=selector,
            delay=delay,
            timeout=timeout,
            wait_until=wait_until,  # type: ignore[arg-type]
            wait_for_selector=wait_for_selector,
            dark_mode=dark_mode,
            reduced_motion=reduced_motion,
            css=css,
            javascript=javascript,
            hide_selectors=hide_selectors,
            click_selector=click_selector,
            block_ads=block_ads,
            block_trackers=block_trackers,
            block_cookie_banners=block_cookie_banners,
            block_chat_widgets=block_chat_widgets,
            user_agent=user_agent,
            extra_headers=extra_headers,
            cookies=cookies,
            http_auth=http_auth,
            proxy=proxy,
            premium_proxy=premium_proxy,
            geolocation=geolocation,
            timezone=timezone,
            storage=storage,
            webhook_url=webhook_url,
            job_id=job_id,
            page_size=page_size,
            landscape=landscape,
            margins=margins,
        )

        raw = await self._request("POST", "/v1/screenshot", opts.to_dict())
        if storage is not None or webhook_url is not None or job_id is not None:
            return json.loads(raw)
        return raw

    async def screenshot_to_storage(
        self,
        url: str,
        destination: str = "snapapi",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Capture a screenshot and store it in SnapAPI cloud (or your S3) asynchronously.

        Args:
            url: The URL to capture.
            destination: Storage destination -- ``'snapapi'`` (default) or ``'user_s3'``.
            **kwargs: Additional screenshot options.

        Returns:
            A dict with at minimum ``'url'`` pointing to the stored file.

        Example::

            result = await snap.screenshot_to_storage("https://example.com")
            print(result["url"])  # Public CDN URL
        """
        kwargs.pop("storage", None)
        result = await self.screenshot(url=url, storage={"destination": destination}, **kwargs)
        if not isinstance(result, dict):
            raise TypeError(
                "screenshot_to_storage: expected JSON response but got binary."
            )
        return result

    async def screenshot_to_file(
        self,
        url: str,
        filepath: str,
        **kwargs: Any,
    ) -> bytes:
        """Capture a screenshot and save it to a file asynchronously.

        Args:
            url: The URL to capture.
            filepath: Destination file path.
            **kwargs: Additional screenshot options.

        Returns:
            The raw bytes that were written to disk.
        """
        kwargs.pop("storage", None)
        kwargs.pop("webhook_url", None)
        kwargs.pop("job_id", None)

        result = await self.screenshot(url=url, **kwargs)
        if not isinstance(result, bytes):
            raise TypeError(
                "screenshot_to_file: expected binary response but got dict."
            )
        Path(filepath).write_bytes(result)
        return result

    # -- PDF ---------------------------------------------------------------------

    async def pdf(
        self,
        url: Optional[str] = None,
        html: Optional[str] = None,
        page_size: str = "a4",
        landscape: bool = False,
        margins: Optional[Dict[str, str]] = None,
        header_template: Optional[str] = None,
        footer_template: Optional[str] = None,
        display_header_footer: bool = False,
        scale: Optional[float] = None,
        delay: int = 0,
        wait_for_selector: Optional[str] = None,
    ) -> bytes:
        """Convert a URL or HTML string to a PDF asynchronously.

        Args and returns are identical to :meth:`SnapAPI.pdf`.
        """
        if not url and not html:
            raise ValueError("One of url or html is required")

        payload: Dict[str, Any] = {"format": "pdf", "pageSize": page_size}
        if url:
            payload["url"] = url
        if html:
            payload["html"] = html
        if landscape:
            payload["landscape"] = True
        if margins:
            payload["margins"] = margins
        if header_template:
            payload["headerTemplate"] = header_template
        if footer_template:
            payload["footerTemplate"] = footer_template
        if display_header_footer:
            payload["displayHeaderFooter"] = True
        if scale is not None:
            payload["scale"] = scale
        if delay > 0:
            payload["delay"] = delay
        if wait_for_selector:
            payload["waitForSelector"] = wait_for_selector

        return await self._request("POST", "/v1/screenshot", payload)

    async def pdf_to_file(
        self,
        url: str,
        filepath: str,
        **kwargs: Any,
    ) -> bytes:
        """Generate a PDF and save it to a file asynchronously.

        Args:
            url: The URL to convert.
            filepath: Destination file path.
            **kwargs: Additional PDF options.

        Returns:
            The raw PDF bytes that were written to disk.
        """
        result = await self.pdf(url=url, **kwargs)
        Path(filepath).write_bytes(result)
        return result

    # -- Scrape ------------------------------------------------------------------

    async def scrape(
        self,
        url: str,
        type: str = "text",
        pages: int = 1,
        wait_ms: Optional[int] = None,
        proxy: Optional[str] = None,
        premium_proxy: Optional[bool] = None,
        block_resources: bool = False,
        locale: Optional[str] = None,
    ) -> ScrapeResult:
        """Scrape text, HTML, or links asynchronously.

        Args and returns are identical to :meth:`SnapAPI.scrape`.
        """
        opts = ScrapeOptions(
            url=url,
            pages=pages,
            type=type,  # type: ignore[arg-type]
            wait_ms=wait_ms,
            proxy=proxy,
            premium_proxy=premium_proxy,
            block_resources=block_resources,
            locale=locale,
        )
        raw = await self._request("POST", "/v1/scrape", opts.to_dict())
        return ScrapeResult.from_dict(json.loads(raw))

    # -- Extract -----------------------------------------------------------------

    async def extract(
        self,
        url: str,
        type: str = "markdown",
        selector: Optional[str] = None,
        wait_for: Optional[str] = None,
        timeout: Optional[int] = None,
        dark_mode: bool = False,
        block_ads: bool = False,
        block_cookie_banners: bool = False,
        include_images: Optional[bool] = None,
        max_length: Optional[int] = None,
        clean_output: Optional[bool] = None,
    ) -> ExtractResult:
        """Extract content asynchronously.

        Args and returns are identical to :meth:`SnapAPI.extract`.
        """
        opts = ExtractOptions(
            url=url,
            type=type,  # type: ignore[arg-type]
            selector=selector,
            wait_for=wait_for,
            timeout=timeout,
            dark_mode=dark_mode,
            block_ads=block_ads,
            block_cookie_banners=block_cookie_banners,
            include_images=include_images,
            max_length=max_length,
            clean_output=clean_output,
        )
        raw = await self._request("POST", "/v1/extract", opts.to_dict())
        return ExtractResult.from_dict(json.loads(raw))

    # -- Extract convenience methods ---------------------------------------------

    async def extract_markdown(self, url: str, **kwargs: Any) -> "ExtractResult":
        """Extract page content as Markdown asynchronously.

        Convenience wrapper for ``extract(url, type='markdown', ...)``.

        Args:
            url: URL to extract from.
            **kwargs: Additional :meth:`extract` options.
        """
        kwargs.pop("type", None)
        return await self.extract(url=url, type="markdown", **kwargs)

    async def extract_article(self, url: str, **kwargs: Any) -> "ExtractResult":
        """Extract main article body asynchronously.

        Convenience wrapper for ``extract(url, type='article', ...)``.
        """
        kwargs.pop("type", None)
        return await self.extract(url=url, type="article", **kwargs)

    async def extract_text(self, url: str, **kwargs: Any) -> "ExtractResult":
        """Extract plain text asynchronously.

        Convenience wrapper for ``extract(url, type='text', ...)``.
        """
        kwargs.pop("type", None)
        return await self.extract(url=url, type="text", **kwargs)

    async def extract_links(self, url: str, **kwargs: Any) -> "ExtractResult":
        """Extract all hyperlinks asynchronously.

        Convenience wrapper for ``extract(url, type='links', ...)``.
        """
        kwargs.pop("type", None)
        return await self.extract(url=url, type="links", **kwargs)

    async def extract_images(self, url: str, **kwargs: Any) -> "ExtractResult":
        """Extract all image URLs asynchronously.

        Convenience wrapper for ``extract(url, type='images', ...)``.
        """
        kwargs.pop("type", None)
        return await self.extract(url=url, type="images", **kwargs)

    async def extract_metadata(self, url: str, **kwargs: Any) -> "ExtractResult":
        """Extract page metadata asynchronously.

        Convenience wrapper for ``extract(url, type='metadata', ...)``.
        """
        kwargs.pop("type", None)
        return await self.extract(url=url, type="metadata", **kwargs)

    # -- Video -------------------------------------------------------------------

    async def video(
        self,
        url: str,
        format: str = "mp4",
        width: int = 1280,
        height: int = 720,
        duration: int = 5,
        fps: int = 25,
        scrolling: bool = False,
        scroll_speed: Optional[int] = None,
        scroll_delay: Optional[int] = None,
        scroll_duration: Optional[int] = None,
        scroll_by: Optional[int] = None,
        scroll_easing: Optional[str] = None,
        scroll_back: bool = True,
        scroll_complete: bool = True,
        dark_mode: bool = False,
        block_ads: bool = False,
        block_cookie_banners: bool = False,
        delay: int = 0,
    ) -> bytes:
        """Record a video asynchronously.

        Args and returns are identical to :meth:`SnapAPI.video`.
        """
        opts = VideoOptions(
            url=url,
            format=format,  # type: ignore[arg-type]
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            scrolling=scrolling,
            scroll_speed=scroll_speed,
            scroll_delay=scroll_delay,
            scroll_duration=scroll_duration,
            scroll_by=scroll_by,
            scroll_easing=scroll_easing,  # type: ignore[arg-type]
            scroll_back=scroll_back,
            scroll_complete=scroll_complete,
            dark_mode=dark_mode,
            block_ads=block_ads,
            block_cookie_banners=block_cookie_banners,
            delay=delay,
        )
        return await self._request("POST", "/v1/video", opts.to_dict())

    # -- OG Image ----------------------------------------------------------------

    async def og_image(
        self,
        url: str,
        format: str = "png",
        width: int = 1200,
        height: int = 630,
    ) -> bytes:
        """Generate an OG image asynchronously."""
        return await self._request(
            "POST",
            "/v1/screenshot",
            {"url": url, "format": format, "width": width, "height": height},
        )

    # -- Analyze -----------------------------------------------------------------

    async def analyze(
        self,
        url: str,
        prompt: str,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        include_screenshot: Optional[bool] = None,
        include_metadata: Optional[bool] = None,
        max_content_length: Optional[int] = None,
        timeout: Optional[int] = None,
        block_ads: bool = False,
        block_cookie_banners: bool = False,
        wait_for: Optional[str] = None,
    ) -> "AnalyzeResult":
        """Analyze a web page with an LLM asynchronously."""
        opts = AnalyzeOptions(
            url=url,
            prompt=prompt,
            provider=provider,  # type: ignore[arg-type]
            api_key=api_key,
            model=model,
            json_schema=json_schema,
            include_screenshot=include_screenshot,
            include_metadata=include_metadata,
            max_content_length=max_content_length,
            timeout=timeout,
            block_ads=block_ads,
            block_cookie_banners=block_cookie_banners,
            wait_for=wait_for,
        )
        raw = await self._request("POST", "/v1/analyze", opts.to_dict())
        return AnalyzeResult.from_dict(json.loads(raw))

    # -- Usage / Quota -----------------------------------------------------------

    async def get_usage(self) -> UsageResult:
        """Get your API usage asynchronously."""
        raw = await self._request("GET", "/v1/usage")
        return UsageResult.from_dict(json.loads(raw))

    async def quota(self) -> UsageResult:
        """Alias for :meth:`get_usage`."""
        return await self.get_usage()

    async def ping(self) -> Dict[str, Any]:
        """Check API availability asynchronously."""
        raw = await self._request("GET", "/v1/ping")
        return json.loads(raw)  # type: ignore[no-any-return]

    # -- Storage -----------------------------------------------------------------

    async def storage_list_files(self, limit: int = 50, offset: int = 0) -> StorageListResult:
        """List stored files asynchronously."""
        raw = await self._request("GET", f"/v1/storage/files?limit={limit}&offset={offset}")
        return StorageListResult.from_dict(json.loads(raw))

    async def storage_get_file(self, file_id: str) -> StorageFile:
        """Get a stored file asynchronously."""
        raw = await self._request("GET", f"/v1/storage/files/{file_id}")
        return StorageFile.from_dict(json.loads(raw))

    async def storage_delete_file(self, file_id: str) -> DeleteResult:
        """Delete a stored file asynchronously."""
        raw = await self._request("DELETE", f"/v1/storage/files/{file_id}")
        return DeleteResult.from_dict(json.loads(raw))

    async def storage_get_usage(self) -> StorageUsage:
        """Get storage usage asynchronously."""
        raw = await self._request("GET", "/v1/storage/usage")
        return StorageUsage.from_dict(json.loads(raw))

    async def storage_configure_s3(self, config: S3Config) -> Dict[str, Any]:
        """Configure S3 asynchronously."""
        raw = await self._request("POST", "/v1/storage/s3", config.to_dict())
        return json.loads(raw)  # type: ignore[no-any-return]

    async def storage_test_s3(self) -> S3TestResult:
        """Test S3 connection asynchronously."""
        raw = await self._request("POST", "/v1/storage/s3/test", {})
        return S3TestResult.from_dict(json.loads(raw))

    # -- Scheduled ---------------------------------------------------------------

    async def scheduled_create(self, options: CreateScheduledOptions) -> ScheduledScreenshot:
        """Create a scheduled job asynchronously."""
        raw = await self._request("POST", "/v1/scheduled", options.to_dict())
        return ScheduledScreenshot.from_dict(json.loads(raw))

    async def scheduled_list(self) -> List[ScheduledScreenshot]:
        """List scheduled jobs asynchronously."""
        raw = await self._request("GET", "/v1/scheduled")
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("jobs", [])
        return [ScheduledScreenshot.from_dict(j) for j in items]

    async def scheduled_delete(self, job_id: str) -> DeleteResult:
        """Delete a scheduled job asynchronously."""
        raw = await self._request("DELETE", f"/v1/scheduled/{job_id}")
        return DeleteResult.from_dict(json.loads(raw))

    # -- Webhooks ----------------------------------------------------------------

    async def webhooks_create(self, options: CreateWebhookOptions) -> Webhook:
        """Register a webhook asynchronously."""
        raw = await self._request("POST", "/v1/webhooks", options.to_dict())
        return Webhook.from_dict(json.loads(raw))

    async def webhooks_list(self) -> List[Webhook]:
        """List webhooks asynchronously."""
        raw = await self._request("GET", "/v1/webhooks")
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("webhooks", [])
        return [Webhook.from_dict(w) for w in items]

    async def webhooks_delete(self, webhook_id: str) -> DeleteResult:
        """Delete a webhook asynchronously."""
        raw = await self._request("DELETE", f"/v1/webhooks/{webhook_id}")
        return DeleteResult.from_dict(json.loads(raw))

    # -- API Keys ----------------------------------------------------------------

    async def keys_list(self) -> List[ApiKey]:
        """List API keys asynchronously."""
        raw = await self._request("GET", "/v1/keys")
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("keys", [])
        return [ApiKey.from_dict(k) for k in items]

    async def keys_create(self, name: str) -> CreateApiKeyResult:
        """Create an API key asynchronously."""
        raw = await self._request("POST", "/v1/keys", {"name": name})
        return CreateApiKeyResult.from_dict(json.loads(raw))

    async def keys_delete(self, key_id: str) -> DeleteResult:
        """Delete an API key asynchronously."""
        raw = await self._request("DELETE", f"/v1/keys/{key_id}")
        return DeleteResult.from_dict(json.loads(raw))

    # -- Internal HTTP -----------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """Execute an async HTTP request with retry logic."""
        url = f"{self.base_url}{path}"
        content = json.dumps(data).encode() if data is not None else None
        client = self._get_client()

        attempt = 0
        while True:
            try:
                resp = await client.request(method, url, content=content)
            except httpx.TimeoutException as exc:
                error: SnapAPIError = TimeoutError(f"Request timed out: {exc}")
                if attempt < self.max_retries and should_retry(error):
                    attempt += 1
                    await asyncio.sleep(compute_backoff(attempt, self.retry_delay))
                    continue
                raise error from exc
            except httpx.RequestError as exc:
                error = NetworkError(f"Network error: {exc}")
                if attempt < self.max_retries and should_retry(error):
                    attempt += 1
                    await asyncio.sleep(compute_backoff(attempt, self.retry_delay))
                    continue
                raise error from exc

            if resp.status_code >= 400:
                parsed = parse_error_response(
                    resp.status_code,
                    resp.content,
                    dict(resp.headers),
                )
                if attempt < self.max_retries and should_retry(parsed):
                    if hasattr(parsed, "retry_after"):
                        wait = min(parsed.retry_after, 30.0)  # type: ignore[attr-defined]
                    else:
                        wait = compute_backoff(attempt + 1, self.retry_delay)
                    attempt += 1
                    await asyncio.sleep(wait)
                    continue
                raise parsed

            return resp.content
