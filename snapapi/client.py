"""
Synchronous SnapAPI client.

Uses ``httpx`` for HTTP transport, which supports connection pooling,
timeouts, and HTTP/2.

Example::

    from snapapi import SnapAPI

    with SnapAPI(api_key="sk_live_...") as snap:
        buf = snap.screenshot(url="https://example.com")
        with open("shot.png", "wb") as f:
            f.write(buf)
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError as exc:
    raise ImportError(
        "httpx is required for SnapAPI: pip install httpx"
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


class SnapAPI:
    """Synchronous SnapAPI client.

    Supports the context-manager protocol::

        with SnapAPI(api_key="sk_live_...") as snap:
            buf = snap.screenshot(url="https://example.com")

    Args:
        api_key: Your SnapAPI key (required).
        base_url: Override the API base URL.
        timeout: Request timeout in seconds (default: 60).
        max_retries: Maximum automatic retries on 429 / 5xx (default: 3).
        retry_delay: Initial backoff delay in seconds (default: 0.5).
            Doubles each retry up to 30 s.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float | None = None,
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

        self._client = httpx.Client(
            timeout=self.timeout,
            headers=build_headers(self.api_key),
        )

    # -- Context manager ---------------------------------------------------------

    def __enter__(self) -> SnapAPI:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    # -- Screenshot --------------------------------------------------------------

    def screenshot(
        self,
        url: str | None = None,
        html: str | None = None,
        markdown: str | None = None,
        format: str = "png",
        quality: int | None = None,
        device: DevicePreset | None = None,
        width: int = 1280,
        height: int = 800,
        device_scale_factor: float = 1.0,
        is_mobile: bool = False,
        has_touch: bool = False,
        full_page: bool = False,
        full_page_scroll_delay: int | None = None,
        full_page_max_height: int | None = None,
        selector: str | None = None,
        delay: int = 0,
        timeout: int | None = None,
        wait_until: str | None = None,
        wait_for_selector: str | None = None,
        dark_mode: bool = False,
        reduced_motion: bool = False,
        css: str | None = None,
        javascript: str | None = None,
        hide_selectors: list[str] | None = None,
        click_selector: str | None = None,
        block_ads: bool = False,
        block_trackers: bool = False,
        block_cookie_banners: bool = False,
        block_chat_widgets: bool = False,
        user_agent: str | None = None,
        extra_headers: dict[str, str] | None = None,
        cookies: list[Cookie] | None = None,
        http_auth: HttpAuth | None = None,
        proxy: ProxyConfig | None = None,
        premium_proxy: bool | None = None,
        geolocation: Geolocation | None = None,
        timezone: str | None = None,
        storage: dict[str, Any] | None = None,
        webhook_url: str | None = None,
        job_id: str | None = None,
        page_size: str | None = None,
        landscape: bool | None = None,
        margins: dict[str, str] | None = None,
    ) -> bytes | dict[str, Any]:
        """Capture a screenshot of a URL, HTML, or Markdown string.

        Args:
            url: Page URL to capture. Required unless ``html`` or ``markdown`` is set.
            html: Raw HTML string to render.
            markdown: Markdown string to render.
            format: Output format -- ``'png'``, ``'jpeg'``, ``'webp'``, ``'avif'``,
                or ``'pdf'``.
            quality: Image quality 1-100 (JPEG / WebP only).
            device: Named device viewport preset (overrides width / height).
            width: Viewport width in pixels (default: 1280).
            height: Viewport height in pixels (default: 800).
            device_scale_factor: Device pixel ratio 1-3 (default: 1.0).
            is_mobile: Emulate a mobile device.
            has_touch: Enable touch events.
            full_page: Capture the full scrollable page.
            full_page_scroll_delay: Delay between scroll steps (ms).
            full_page_max_height: Maximum height for full-page capture (px).
            selector: CSS selector -- capture only that element.
            delay: Extra delay before capture in ms (0-30 000).
            timeout: Navigation timeout in ms.
            wait_until: Navigation event to wait for.
            wait_for_selector: Wait for this CSS selector to appear.
            dark_mode: Emulate dark colour scheme.
            reduced_motion: Reduce CSS animations.
            css: Custom CSS to inject into the page.
            javascript: JavaScript to execute before capturing.
            hide_selectors: CSS selectors to hide (visibility: hidden).
            click_selector: CSS selector to click before capturing.
            block_ads: Block ad networks.
            block_trackers: Block tracking scripts.
            block_cookie_banners: Block cookie consent banners.
            block_chat_widgets: Block chat widgets.
            user_agent: Custom User-Agent string.
            extra_headers: Extra HTTP request headers.
            cookies: Cookies to inject.
            http_auth: HTTP Basic Auth credentials.
            proxy: Custom proxy configuration.
            premium_proxy: Use SnapAPI rotating proxy.
            geolocation: GPS coordinates to emulate.
            timezone: IANA timezone string.
            storage: Store result in cloud (``{'destination': 'snapapi'}``).
            webhook_url: Deliver result to this webhook URL asynchronously.
            job_id: Poll a previously queued async job.
            page_size: PDF page size (e.g. ``'a4'``, ``'letter'``).
            landscape: PDF landscape orientation.
            margins: PDF page margins dict with keys top/right/bottom/left.

        Returns:
            ``bytes`` for binary image / PDF responses.
            ``dict`` when ``storage`` or ``webhook_url`` is set.

        Raises:
            ValueError: When no input source (url / html / markdown) is given.
            SnapAPIError: On API errors.
            AuthenticationError: On HTTP 401 / 403.
            RateLimitError: On HTTP 429 (auto-retried up to ``max_retries``).
            QuotaExceededError: On HTTP 402 quota error.
            TimeoutError: When the request times out.
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

        raw = self._request("POST", "/v1/screenshot", opts.to_dict())

        if storage is not None or webhook_url is not None or job_id is not None:
            return json.loads(raw)
        return raw

    def screenshot_to_storage(
        self,
        url: str,
        destination: str = "snapapi",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Capture a screenshot and store it in SnapAPI cloud (or your S3).

        Args:
            url: The URL to capture.
            destination: Storage destination -- ``'snapapi'`` (default) or ``'user_s3'``.
            **kwargs: Additional screenshot options (format, full_page, etc.).

        Returns:
            A dict with at minimum ``'url'`` pointing to the stored file.

        Example::

            result = snap.screenshot_to_storage("https://example.com")
            print(result["url"])  # Public CDN URL
        """
        kwargs.pop("storage", None)
        result = self.screenshot(url=url, storage={"destination": destination}, **kwargs)
        if not isinstance(result, dict):
            raise TypeError(
                "screenshot_to_storage: expected JSON response but got binary. "
                "Check that the destination is valid."
            )
        return result

    def screenshot_to_file(
        self,
        url: str,
        filepath: str,
        **kwargs: Any,
    ) -> bytes:
        """Capture a screenshot and save it directly to a file.

        This is a convenience wrapper around :meth:`screenshot` that handles
        file I/O for you.

        Args:
            url: The URL to capture.
            filepath: Destination file path (e.g. ``'./output/shot.png'``).
            **kwargs: Additional screenshot options (format, full_page, etc.).

        Returns:
            The raw bytes that were written to disk.

        Example::

            snap.screenshot_to_file("https://example.com", "./shot.png")
            snap.screenshot_to_file(
                "https://example.com", "./full.webp",
                format="webp", full_page=True,
            )
        """
        # Remove storage/webhook options that would change the return type
        kwargs.pop("storage", None)
        kwargs.pop("webhook_url", None)
        kwargs.pop("job_id", None)

        result = self.screenshot(url=url, **kwargs)
        if not isinstance(result, bytes):
            raise TypeError(
                "screenshot_to_file: expected binary response but got dict. "
                "Do not use storage or webhook_url options."
            )
        Path(filepath).write_bytes(result)
        return result

    # -- PDF ---------------------------------------------------------------------

    def pdf(
        self,
        url: str | None = None,
        html: str | None = None,
        page_size: str = "a4",
        landscape: bool = False,
        margins: dict[str, str] | None = None,
        header_template: str | None = None,
        footer_template: str | None = None,
        display_header_footer: bool = False,
        scale: float | None = None,
        delay: int = 0,
        wait_for_selector: str | None = None,
    ) -> bytes:
        """Convert a URL or HTML string to a PDF file.

        Args:
            url: Page URL to convert. Required unless ``html`` is set.
            html: Raw HTML string to convert.
            page_size: PDF page size (default: ``'a4'``).
            landscape: Landscape orientation (default: ``False``).
            margins: Page margins dict with keys top/right/bottom/left.
            header_template: HTML template for the page header.
            footer_template: HTML template for the page footer.
            display_header_footer: Show header and footer.
            scale: Content scale factor 0.1-2.
            delay: Extra delay before rendering (ms).
            wait_for_selector: CSS selector to wait for before rendering.

        Returns:
            Raw PDF bytes.

        Raises:
            ValueError: When neither ``url`` nor ``html`` is provided.
        """
        if not url and not html:
            raise ValueError("One of url or html is required")

        payload: dict[str, Any] = {"format": "pdf", "pageSize": page_size}
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

        return self._request("POST", "/v1/screenshot", payload)

    def pdf_to_file(
        self,
        url: str,
        filepath: str,
        **kwargs: Any,
    ) -> bytes:
        """Generate a PDF and save it directly to a file.

        Args:
            url: The URL to convert.
            filepath: Destination file path (e.g. ``'./output.pdf'``).
            **kwargs: Additional PDF options (page_size, landscape, etc.).

        Returns:
            The raw PDF bytes that were written to disk.

        Example::

            snap.pdf_to_file("https://example.com", "./output.pdf", page_size="letter")
        """
        result = self.pdf(url=url, **kwargs)
        Path(filepath).write_bytes(result)
        return result

    # -- Scrape ------------------------------------------------------------------

    def scrape(
        self,
        url: str,
        type: str = "text",
        pages: int = 1,
        wait_ms: int | None = None,
        proxy: str | None = None,
        premium_proxy: bool | None = None,
        block_resources: bool = False,
        locale: str | None = None,
    ) -> ScrapeResult:
        """Scrape text, HTML, or links from one or more pages.

        Args:
            url: URL to scrape (required).
            type: Content type -- ``'text'``, ``'html'``, or ``'links'``.
            pages: Number of pages to scrape, 1-10 (default: 1).
            wait_ms: Wait time after page load in ms.
            proxy: Proxy URL e.g. ``'http://user:pass@host:port'``.
            premium_proxy: Use SnapAPI rotating proxy.
            block_resources: Block images / fonts / media.
            locale: Browser locale e.g. ``'en-US'``.

        Returns:
            :class:`ScrapeResult` with a list of scraped page results.

        Example::

            result = snap.scrape(url="https://example.com", type="links")
            for page in result.results:
                print(page.data)
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
        raw = self._request("POST", "/v1/scrape", opts.to_dict())
        return ScrapeResult.from_dict(json.loads(raw))

    # -- Extract -----------------------------------------------------------------

    def extract(
        self,
        url: str,
        type: str = "markdown",
        selector: str | None = None,
        wait_for: str | None = None,
        timeout: int | None = None,
        dark_mode: bool = False,
        block_ads: bool = False,
        block_cookie_banners: bool = False,
        include_images: bool | None = None,
        max_length: int | None = None,
        clean_output: bool | None = None,
    ) -> ExtractResult:
        """Extract structured content from a web page.

        Args:
            url: URL to extract content from (required).
            type: Extraction type -- ``'markdown'``, ``'text'``, ``'html'``,
                ``'article'``, ``'links'``, ``'images'``, ``'metadata'``,
                or ``'structured'``.
            selector: CSS selector to scope the extraction.
            wait_for: CSS selector to wait for before extracting.
            timeout: Navigation timeout in ms.
            dark_mode: Emulate dark mode.
            block_ads: Block ad networks.
            block_cookie_banners: Block cookie consent banners.
            include_images: Include image URLs in extracted output.
            max_length: Truncate output at this many characters.
            clean_output: Strip navigation and boilerplate.

        Returns:
            :class:`ExtractResult` with the extracted content.

        Example::

            result = snap.extract(url="https://example.com", type="markdown")
            print(result.content)
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
        raw = self._request("POST", "/v1/extract", opts.to_dict())
        return ExtractResult.from_dict(json.loads(raw))

    # -- Extract convenience methods ---------------------------------------------

    def extract_markdown(self, url: str, **kwargs: Any) -> ExtractResult:
        """Extract page content as Markdown.

        Convenience wrapper for ``extract(url, type='markdown', ...)``.

        Args:
            url: URL to extract from.
            **kwargs: Additional :meth:`extract` options.

        Returns:
            :class:`ExtractResult` with Markdown content in ``.content``.
        """
        kwargs.pop("type", None)
        return self.extract(url=url, type="markdown", **kwargs)

    def extract_article(self, url: str, **kwargs: Any) -> ExtractResult:
        """Extract main article body from a page.

        Convenience wrapper for ``extract(url, type='article', ...)``.

        Args:
            url: URL to extract from.
            **kwargs: Additional :meth:`extract` options.

        Returns:
            :class:`ExtractResult` with cleaned article content in ``.content``.
        """
        kwargs.pop("type", None)
        return self.extract(url=url, type="article", **kwargs)

    def extract_text(self, url: str, **kwargs: Any) -> ExtractResult:
        """Extract plain text from a page.

        Convenience wrapper for ``extract(url, type='text', ...)``.

        Args:
            url: URL to extract from.
            **kwargs: Additional :meth:`extract` options.

        Returns:
            :class:`ExtractResult` with plain text content in ``.content``.
        """
        kwargs.pop("type", None)
        return self.extract(url=url, type="text", **kwargs)

    def extract_links(self, url: str, **kwargs: Any) -> ExtractResult:
        """Extract all hyperlinks from a page.

        Convenience wrapper for ``extract(url, type='links', ...)``.

        Args:
            url: URL to extract from.
            **kwargs: Additional :meth:`extract` options.

        Returns:
            :class:`ExtractResult` with a list of links in ``.content``.
        """
        kwargs.pop("type", None)
        return self.extract(url=url, type="links", **kwargs)

    def extract_images(self, url: str, **kwargs: Any) -> ExtractResult:
        """Extract all image URLs from a page.

        Convenience wrapper for ``extract(url, type='images', ...)``.

        Args:
            url: URL to extract from.
            **kwargs: Additional :meth:`extract` options.

        Returns:
            :class:`ExtractResult` with a list of image URLs in ``.content``.
        """
        kwargs.pop("type", None)
        return self.extract(url=url, type="images", **kwargs)

    def extract_metadata(self, url: str, **kwargs: Any) -> ExtractResult:
        """Extract page metadata (title, description, OG tags, etc.).

        Convenience wrapper for ``extract(url, type='metadata', ...)``.

        Args:
            url: URL to extract from.
            **kwargs: Additional :meth:`extract` options.

        Returns:
            :class:`ExtractResult` with metadata dict in ``.content``.
        """
        kwargs.pop("type", None)
        return self.extract(url=url, type="metadata", **kwargs)

    # -- Video -------------------------------------------------------------------

    def video(
        self,
        url: str,
        format: str = "mp4",
        width: int = 1280,
        height: int = 720,
        duration: int = 5,
        fps: int = 25,
        scrolling: bool = False,
        scroll_speed: int | None = None,
        scroll_delay: int | None = None,
        scroll_duration: int | None = None,
        scroll_by: int | None = None,
        scroll_easing: str | None = None,
        scroll_back: bool = True,
        scroll_complete: bool = True,
        dark_mode: bool = False,
        block_ads: bool = False,
        block_cookie_banners: bool = False,
        delay: int = 0,
    ) -> bytes:
        """Record a video of a live webpage.

        Args:
            url: URL to record (required).
            format: Output format -- ``'mp4'``, ``'webm'``, or ``'gif'``.
            width: Viewport width 320-1920 (default: 1280).
            height: Viewport height 240-1080 (default: 720).
            duration: Recording duration in seconds 1-30 (default: 5).
            fps: Frames per second 10-30 (default: 25).
            scrolling: Enable automatic scroll animation.
            scroll_speed: Scroll speed in px/s, 50-500.
            scroll_delay: Delay before scroll starts in ms, 0-5000.
            scroll_duration: Duration of each scroll step in ms, 100-5000.
            scroll_by: Pixels to scroll per step, 100-2000.
            scroll_easing: Easing function for scroll.
            scroll_back: Scroll back to top after reaching the bottom.
            scroll_complete: Stop when scroll reaches the bottom.
            dark_mode: Enable dark mode.
            block_ads: Block ad networks.
            block_cookie_banners: Block cookie consent banners.
            delay: Delay before recording starts in ms.

        Returns:
            Raw video bytes.

        Example::

            video = snap.video(url="https://example.com", duration=5)
            with open("recording.mp4", "wb") as f:
                f.write(video)
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
        return self._request("POST", "/v1/video", opts.to_dict())

    # -- OG Image ----------------------------------------------------------------

    def og_image(
        self,
        url: str,
        format: str = "png",
        width: int = 1200,
        height: int = 630,
    ) -> bytes:
        """Generate an Open Graph image for a URL.

        Args:
            url: URL to generate an OG image for (required).
            format: Output format (default: ``'png'``).
            width: Image width (default: 1200).
            height: Image height (default: 630).

        Returns:
            Raw image bytes.

        Example::

            og = snap.og_image(url="https://example.com")
            with open("og.png", "wb") as f:
                f.write(og)
        """
        return self._request(
            "POST",
            "/v1/screenshot",
            {"url": url, "format": format, "width": width, "height": height},
        )

    # -- Analyze -----------------------------------------------------------------

    def analyze(
        self,
        url: str,
        prompt: str,
        provider: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        json_schema: dict[str, Any] | None = None,
        include_screenshot: bool | None = None,
        include_metadata: bool | None = None,
        max_content_length: int | None = None,
        timeout: int | None = None,
        block_ads: bool = False,
        block_cookie_banners: bool = False,
        wait_for: str | None = None,
    ) -> AnalyzeResult:
        """Analyze a web page with an LLM (BYOK -- bring your own key).

        Args:
            url: URL to analyze (required).
            prompt: Analysis prompt (required).
            provider: LLM provider -- ``'openai'`` or ``'anthropic'``.
            api_key: Your LLM provider API key.
            model: Override the default model.
            json_schema: JSON schema for structured output.
            include_screenshot: Include a screenshot in the analysis context.
            include_metadata: Include page metadata in the context.
            max_content_length: Maximum characters of page content to send.
            timeout: Navigation timeout in ms.
            block_ads: Block ad networks.
            block_cookie_banners: Block cookie consent banners.
            wait_for: CSS selector to wait for before analyzing.

        Returns:
            :class:`AnalyzeResult` with the AI-generated analysis.

        Example::

            result = snap.analyze(
                url="https://example.com",
                prompt="Summarize this page in 3 bullet points.",
                provider="openai",
                api_key="sk-...",
            )
            print(result.result)
        """
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
        raw = self._request("POST", "/v1/analyze", opts.to_dict())
        return AnalyzeResult.from_dict(json.loads(raw))

    # -- Usage / Quota -----------------------------------------------------------

    def get_usage(self) -> UsageResult:
        """Get your API usage for the current billing period.

        Returns:
            :class:`UsageResult` with ``used``, ``limit``, ``remaining``,
            and ``reset_at`` fields.

        Example::

            usage = snap.get_usage()
            print(f"{usage.used} / {usage.limit} calls used")
        """
        raw = self._request("GET", "/v1/usage")
        return UsageResult.from_dict(json.loads(raw))

    def quota(self) -> UsageResult:
        """Alias for :meth:`get_usage`.

        Example::

            usage = snap.quota()
        """
        return self.get_usage()

    # -- Ping --------------------------------------------------------------------

    def ping(self) -> dict[str, Any]:
        """Check API availability.

        Returns:
            ``{'status': 'ok', 'timestamp': <unix ms>}``
        """
        raw = self._request("GET", "/v1/ping")
        return json.loads(raw)  # type: ignore[no-any-return]

    # -- Storage -----------------------------------------------------------------

    def storage_list_files(self, limit: int = 50, offset: int = 0) -> StorageListResult:
        """list files stored in SnapAPI cloud.

        Args:
            limit: Maximum results per page (default: 50).
            offset: Pagination offset (default: 0).

        Returns:
            :class:`StorageListResult` with the list of files.
        """
        raw = self._request("GET", f"/v1/storage/files?limit={limit}&offset={offset}")
        return StorageListResult.from_dict(json.loads(raw))

    def storage_get_file(self, file_id: str) -> StorageFile:
        """Get metadata and download URL for a specific stored file.

        Args:
            file_id: The file ID.

        Returns:
            :class:`StorageFile`.
        """
        raw = self._request("GET", f"/v1/storage/files/{file_id}")
        return StorageFile.from_dict(json.loads(raw))

    def storage_delete_file(self, file_id: str) -> DeleteResult:
        """Delete a stored file.

        Args:
            file_id: The file ID.

        Returns:
            :class:`DeleteResult` with ``success`` flag.
        """
        raw = self._request("DELETE", f"/v1/storage/files/{file_id}")
        return DeleteResult.from_dict(json.loads(raw))

    def storage_get_usage(self) -> StorageUsage:
        """Get storage usage for this account.

        Returns:
            :class:`StorageUsage`.
        """
        raw = self._request("GET", "/v1/storage/usage")
        return StorageUsage.from_dict(json.loads(raw))

    def storage_configure_s3(self, config: S3Config) -> dict[str, Any]:
        """Configure a custom S3-compatible storage backend.

        Args:
            config: :class:`S3Config` with bucket, region, credentials,
                and optional endpoint.

        Returns:
            ``{'success': True}``
        """
        raw = self._request("POST", "/v1/storage/s3", config.to_dict())
        return json.loads(raw)  # type: ignore[no-any-return]

    def storage_test_s3(self) -> S3TestResult:
        """Test the configured S3 connection.

        Returns:
            :class:`S3TestResult`.
        """
        raw = self._request("POST", "/v1/storage/s3/test", {})
        return S3TestResult.from_dict(json.loads(raw))

    # -- Scheduled ---------------------------------------------------------------

    def scheduled_create(self, options: CreateScheduledOptions) -> ScheduledScreenshot:
        """Create a new scheduled screenshot job.

        Args:
            options: :class:`CreateScheduledOptions`.

        Returns:
            :class:`ScheduledScreenshot` with ``id`` and ``next_run``.
        """
        raw = self._request("POST", "/v1/scheduled", options.to_dict())
        return ScheduledScreenshot.from_dict(json.loads(raw))

    def scheduled_list(self) -> list[ScheduledScreenshot]:
        """list all scheduled screenshot jobs.

        Returns:
            list of :class:`ScheduledScreenshot`.
        """
        raw = self._request("GET", "/v1/scheduled")
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("jobs", [])
        return [ScheduledScreenshot.from_dict(j) for j in items]

    def scheduled_delete(self, job_id: str) -> DeleteResult:
        """Delete a scheduled screenshot job.

        Args:
            job_id: The job ID.

        Returns:
            :class:`DeleteResult`.
        """
        raw = self._request("DELETE", f"/v1/scheduled/{job_id}")
        return DeleteResult.from_dict(json.loads(raw))

    # -- Webhooks ----------------------------------------------------------------

    def webhooks_create(self, options: CreateWebhookOptions) -> Webhook:
        """Register a new webhook endpoint.

        Args:
            options: :class:`CreateWebhookOptions`.

        Returns:
            :class:`Webhook`.
        """
        raw = self._request("POST", "/v1/webhooks", options.to_dict())
        return Webhook.from_dict(json.loads(raw))

    def webhooks_list(self) -> list[Webhook]:
        """list all registered webhooks.

        Returns:
            list of :class:`Webhook`.
        """
        raw = self._request("GET", "/v1/webhooks")
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("webhooks", [])
        return [Webhook.from_dict(w) for w in items]

    def webhooks_delete(self, webhook_id: str) -> DeleteResult:
        """Delete a webhook.

        Args:
            webhook_id: The webhook ID.

        Returns:
            :class:`DeleteResult`.
        """
        raw = self._request("DELETE", f"/v1/webhooks/{webhook_id}")
        return DeleteResult.from_dict(json.loads(raw))

    # -- API Keys ----------------------------------------------------------------

    def keys_list(self) -> list[ApiKey]:
        """list all API keys. Key values are masked.

        Returns:
            list of :class:`ApiKey`.
        """
        raw = self._request("GET", "/v1/keys")
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("keys", [])
        return [ApiKey.from_dict(k) for k in items]

    def keys_create(self, name: str) -> CreateApiKeyResult:
        """Create a new API key. The full key is returned only once.

        Args:
            name: Human-readable label for the key.

        Returns:
            :class:`CreateApiKeyResult` with the full key value.
        """
        raw = self._request("POST", "/v1/keys", {"name": name})
        return CreateApiKeyResult.from_dict(json.loads(raw))

    def keys_delete(self, key_id: str) -> DeleteResult:
        """Delete an API key.

        Args:
            key_id: The key ID.

        Returns:
            :class:`DeleteResult`.
        """
        raw = self._request("DELETE", f"/v1/keys/{key_id}")
        return DeleteResult.from_dict(json.loads(raw))

    # -- Internal HTTP -----------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> bytes:
        """Execute an HTTP request with retry logic.

        Args:
            method: HTTP method (``'GET'``, ``'POST'``, ``'DELETE'``).
            path: API path (e.g. ``'/v1/screenshot'``).
            data: JSON payload.

        Returns:
            Raw response bytes.

        Raises:
            SnapAPIError: On any API error after retries are exhausted.
        """
        url = f"{self.base_url}{path}"
        content = json.dumps(data).encode() if data is not None else None

        attempt = 0
        while True:
            try:
                resp = self._client.request(method, url, content=content)
            except httpx.TimeoutException as exc:
                error: SnapAPIError = TimeoutError(f"Request timed out: {exc}")
                if attempt < self.max_retries and should_retry(error):
                    attempt += 1
                    time.sleep(compute_backoff(attempt, self.retry_delay))
                    continue
                raise error from exc
            except httpx.RequestError as exc:
                error = NetworkError(f"Network error: {exc}")
                if attempt < self.max_retries and should_retry(error):
                    attempt += 1
                    time.sleep(compute_backoff(attempt, self.retry_delay))
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
                    time.sleep(wait)
                    continue
                raise parsed

            return resp.content
