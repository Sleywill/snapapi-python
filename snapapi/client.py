"""
SnapAPI Python Client
"""

import json
from typing import Optional, Union, Dict, Any, List
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .types import (
    ScreenshotOptions,
    ScreenshotResult,
    BatchOptions,
    BatchResult,
    DevicesResult,
    CapabilitiesResult,
    UsageResult,
    Cookie,
    HttpAuth,
    ProxyConfig,
    Geolocation,
    PdfOptions,
    ThumbnailOptions,
    ExtractMetadata,
    DevicePreset,
    VideoOptions,
    VideoResult,
    ScrollEasing,
    ExtractOptions,
    ExtractResult,
    ExtractType,
    AnalyzeOptions,
    AnalyzeResult,
    AnalyzeProvider,
)


class SnapAPIError(Exception):
    """Exception raised for SnapAPI errors."""

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details or {}

    def __str__(self) -> str:
        return f"[{self.code}] {super().__str__()}"


class SnapAPI:
    """
    SnapAPI Client for Python

    Example:
        >>> from snapapi import SnapAPI
        >>> client = SnapAPI(api_key='sk_live_xxx')
        >>> screenshot = client.screenshot(url='https://example.com')
        >>> with open('screenshot.png', 'wb') as f:
        ...     f.write(screenshot)
    """

    DEFAULT_BASE_URL = "https://api.snapapi.pics"
    DEFAULT_TIMEOUT = 60

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        Initialize the SnapAPI client.

        Args:
            api_key: Your SnapAPI API key
            base_url: Optional custom base URL
            timeout: Request timeout in seconds (default: 60)
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    def screenshot(
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
        is_landscape: bool = False,
        full_page: bool = False,
        full_page_scroll_delay: Optional[int] = None,
        full_page_max_height: Optional[int] = None,
        selector: Optional[str] = None,
        clip_x: Optional[int] = None,
        clip_y: Optional[int] = None,
        clip_width: Optional[int] = None,
        clip_height: Optional[int] = None,
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
        click_delay: Optional[int] = None,
        block_ads: bool = False,
        block_trackers: bool = False,
        block_cookie_banners: bool = False,
        block_chat_widgets: bool = False,
        block_resources: Optional[List[str]] = None,
        user_agent: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        cookies: Optional[List[Cookie]] = None,
        http_auth: Optional[HttpAuth] = None,
        proxy: Optional[ProxyConfig] = None,
        geolocation: Optional[Geolocation] = None,
        timezone: Optional[str] = None,
        locale: Optional[str] = None,
        pdf_options: Optional[PdfOptions] = None,
        thumbnail: Optional[ThumbnailOptions] = None,
        fail_on_http_error: bool = False,
        cache: bool = False,
        cache_ttl: Optional[int] = None,
        response_type: str = "binary",
        include_metadata: bool = False,
        extract_metadata: Optional[ExtractMetadata] = None,
    ) -> Union[bytes, ScreenshotResult]:
        """
        Capture a screenshot of the specified URL, HTML, or Markdown content.

        Args:
            url: URL to capture (required if no html/markdown)
            html: HTML content to render (required if no url/markdown)
            markdown: Markdown content to render (required if no url/html)
            format: Output format ('png', 'jpeg', 'webp', 'avif', 'pdf')
            quality: Image quality 1-100 (JPEG/WebP only)
            device: Device preset name (e.g., 'iphone-15-pro')
            width: Viewport width (100-3840)
            height: Viewport height (100-2160)
            device_scale_factor: Device pixel ratio (1-3)
            is_mobile: Emulate mobile device
            has_touch: Enable touch events
            is_landscape: Landscape orientation
            full_page: Capture full scrollable page
            full_page_scroll_delay: Delay between scroll steps (ms)
            full_page_max_height: Max height for full page (px)
            selector: CSS selector for element capture
            clip_x, clip_y: Clip region position
            clip_width, clip_height: Clip region size
            delay: Delay before capture in ms (0-30000)
            timeout: Max wait time in ms (1000-60000)
            wait_until: Wait event ('load', 'domcontentloaded', 'networkidle')
            wait_for_selector: Wait for element before capture
            dark_mode: Emulate dark mode
            reduced_motion: Reduce animations
            css: Custom CSS to inject
            javascript: JS to execute before capture
            hide_selectors: CSS selectors to hide
            click_selector: Element to click before capture
            click_delay: Delay after click (ms)
            block_ads: Block ads
            block_trackers: Block trackers
            block_cookie_banners: Hide cookie consent banners
            block_chat_widgets: Block chat widgets (Intercom, Drift, etc.)
            block_resources: Resource types to block
            user_agent: Custom User-Agent
            extra_headers: Custom HTTP headers
            cookies: Cookies to set
            http_auth: HTTP basic auth credentials
            proxy: Proxy configuration
            geolocation: Geolocation coordinates
            timezone: Timezone (e.g., 'America/New_York')
            locale: Locale (e.g., 'en-US')
            pdf_options: PDF generation options
            thumbnail: Thumbnail generation options
            fail_on_http_error: Fail on 4xx/5xx responses
            cache: Enable caching
            cache_ttl: Cache TTL in seconds
            response_type: 'binary', 'base64', or 'json'
            include_metadata: Include page metadata
            extract_metadata: Additional metadata to extract

        Returns:
            bytes if response_type is 'binary', ScreenshotResult otherwise
        """
        if not url and not html and not markdown:
            raise ValueError("Either url, html, or markdown is required")

        options = ScreenshotOptions(
            url=url,
            html=html,
            markdown=markdown,
            format=format,
            quality=quality,
            device=device,
            width=width,
            height=height,
            device_scale_factor=device_scale_factor,
            is_mobile=is_mobile,
            has_touch=has_touch,
            is_landscape=is_landscape,
            full_page=full_page,
            full_page_scroll_delay=full_page_scroll_delay,
            full_page_max_height=full_page_max_height,
            selector=selector,
            clip_x=clip_x,
            clip_y=clip_y,
            clip_width=clip_width,
            clip_height=clip_height,
            delay=delay,
            timeout=timeout,
            wait_until=wait_until,
            wait_for_selector=wait_for_selector,
            dark_mode=dark_mode,
            reduced_motion=reduced_motion,
            css=css,
            javascript=javascript,
            hide_selectors=hide_selectors,
            click_selector=click_selector,
            click_delay=click_delay,
            block_ads=block_ads,
            block_trackers=block_trackers,
            block_cookie_banners=block_cookie_banners,
            block_chat_widgets=block_chat_widgets,
            block_resources=block_resources,
            user_agent=user_agent,
            extra_headers=extra_headers,
            cookies=cookies,
            http_auth=http_auth,
            proxy=proxy,
            geolocation=geolocation,
            timezone=timezone,
            locale=locale,
            pdf_options=pdf_options,
            thumbnail=thumbnail,
            fail_on_http_error=fail_on_http_error,
            cache=cache,
            cache_ttl=cache_ttl,
            response_type=response_type,
            include_metadata=include_metadata,
            extract_metadata=extract_metadata,
        )

        response = self._request("POST", "/v1/screenshot", options.to_dict())

        if response_type == "binary":
            return response
        elif response_type in ("json", "base64"):
            return ScreenshotResult.from_dict(json.loads(response))
        else:
            return response

    def screenshot_from_html(
        self, html: str, **kwargs
    ) -> Union[bytes, ScreenshotResult]:
        """
        Capture a screenshot from HTML content.

        Args:
            html: HTML content to render
            **kwargs: Additional screenshot options

        Returns:
            bytes if response_type is 'binary', ScreenshotResult otherwise
        """
        return self.screenshot(html=html, **kwargs)

    def screenshot_device(
        self, url: str, device: DevicePreset, **kwargs
    ) -> Union[bytes, ScreenshotResult]:
        """
        Capture a screenshot using a device preset.

        Args:
            url: URL to capture
            device: Device preset name (e.g., 'iphone-15-pro')
            **kwargs: Additional screenshot options

        Returns:
            bytes if response_type is 'binary', ScreenshotResult otherwise
        """
        return self.screenshot(url=url, device=device, **kwargs)

    def screenshot_from_markdown(
        self, markdown: str, **kwargs
    ) -> Union[bytes, ScreenshotResult]:
        """
        Capture a screenshot from Markdown content.

        Args:
            markdown: Markdown content to render
            **kwargs: Additional screenshot options

        Returns:
            bytes if response_type is 'binary', ScreenshotResult otherwise
        """
        return self.screenshot(markdown=markdown, **kwargs)

    def pdf(
        self,
        url: Optional[str] = None,
        html: Optional[str] = None,
        pdf_options: Optional[PdfOptions] = None,
        **kwargs,
    ) -> bytes:
        """
        Generate a PDF from a URL or HTML content.

        Args:
            url: URL to capture
            html: HTML content to render
            pdf_options: PDF generation options
            **kwargs: Additional screenshot options

        Returns:
            Binary PDF data
        """
        if not url and not html:
            raise ValueError("Either url or html is required")

        kwargs["format"] = "pdf"
        kwargs["response_type"] = "binary"
        if pdf_options:
            kwargs["pdf_options"] = pdf_options

        return self.screenshot(url=url, html=html, **kwargs)

    def video(
        self,
        url: str,
        format: str = "mp4",
        quality: Optional[int] = None,
        width: int = 1280,
        height: int = 720,
        device: Optional[DevicePreset] = None,
        duration: int = 5000,
        fps: int = 24,
        delay: int = 0,
        timeout: int = 60000,
        wait_until: Optional[str] = None,
        wait_for_selector: Optional[str] = None,
        dark_mode: bool = False,
        block_ads: bool = False,
        block_cookie_banners: bool = False,
        css: Optional[str] = None,
        javascript: Optional[str] = None,
        hide_selectors: Optional[List[str]] = None,
        user_agent: Optional[str] = None,
        cookies: Optional[List[Cookie]] = None,
        response_type: str = "binary",
        scroll: bool = False,
        scroll_delay: Optional[int] = None,
        scroll_duration: Optional[int] = None,
        scroll_by: Optional[int] = None,
        scroll_easing: Optional[str] = None,
        scroll_back: bool = False,
        scroll_complete: bool = False,
    ) -> Union[bytes, VideoResult]:
        """
        Capture a video of the specified URL with optional scroll animation.

        Args:
            url: URL to capture
            format: Output format ('mp4', 'webm', 'gif')
            quality: Video quality 1-100
            width: Viewport width (100-1920)
            height: Viewport height (100-1080)
            device: Device preset name
            duration: Video duration in ms (1000-30000)
            fps: Frames per second (1-30)
            delay: Delay before starting capture (ms)
            timeout: Max wait time in ms
            wait_until: Wait event ('load', 'domcontentloaded', 'networkidle')
            wait_for_selector: Wait for element before capture
            dark_mode: Emulate dark mode
            block_ads: Block ads
            block_cookie_banners: Hide cookie consent banners
            css: Custom CSS to inject
            javascript: JS to execute before capture
            hide_selectors: CSS selectors to hide
            user_agent: Custom User-Agent
            cookies: Cookies to set
            response_type: 'binary', 'base64', or 'json'
            scroll: Enable scroll animation video
            scroll_delay: Delay between scroll steps in ms (0-5000)
            scroll_duration: Duration of each scroll animation in ms (100-5000)
            scroll_by: Pixels to scroll each step (100-2000)
            scroll_easing: Easing function ('linear', 'ease_in', 'ease_out', 'ease_in_out', 'ease_in_out_quint')
            scroll_back: Scroll back to top at the end
            scroll_complete: Ensure entire page is scrolled

        Returns:
            bytes if response_type is 'binary', VideoResult otherwise

        Example:
            >>> video = client.video(
            ...     url='https://example.com',
            ...     scroll=True,
            ...     scroll_duration=1500,
            ...     scroll_easing='ease_in_out',
            ...     scroll_back=True
            ... )
            >>> with open('scroll.mp4', 'wb') as f:
            ...     f.write(video)
        """
        options = VideoOptions(
            url=url,
            format=format,
            quality=quality,
            width=width,
            height=height,
            device=device,
            duration=duration,
            fps=fps,
            delay=delay,
            timeout=timeout,
            wait_until=wait_until,
            wait_for_selector=wait_for_selector,
            dark_mode=dark_mode,
            block_ads=block_ads,
            block_cookie_banners=block_cookie_banners,
            css=css,
            javascript=javascript,
            hide_selectors=hide_selectors,
            user_agent=user_agent,
            cookies=cookies,
            response_type=response_type,
            scroll=scroll,
            scroll_delay=scroll_delay,
            scroll_duration=scroll_duration,
            scroll_by=scroll_by,
            scroll_easing=scroll_easing,
            scroll_back=scroll_back,
            scroll_complete=scroll_complete,
        )

        response = self._request("POST", "/v1/video", options.to_dict())

        if response_type == "binary":
            return response
        elif response_type in ("json", "base64"):
            return VideoResult.from_dict(json.loads(response))
        else:
            return response

    def batch(
        self,
        urls: List[str],
        format: str = "png",
        quality: Optional[int] = None,
        width: int = 1280,
        height: int = 800,
        full_page: bool = False,
        webhook_url: Optional[str] = None,
        dark_mode: bool = False,
        block_ads: bool = False,
        block_cookie_banners: bool = False,
    ) -> BatchResult:
        """
        Capture screenshots of multiple URLs.

        Args:
            urls: List of URLs to capture
            format: Output format
            quality: Image quality
            width: Viewport width
            height: Viewport height
            full_page: Capture full page
            webhook_url: URL for async notifications
            dark_mode: Emulate dark mode
            block_ads: Block ads
            block_cookie_banners: Hide cookie banners

        Returns:
            BatchResult with job ID and status
        """
        options = BatchOptions(
            urls=urls,
            format=format,
            quality=quality,
            width=width,
            height=height,
            full_page=full_page,
            webhook_url=webhook_url,
            dark_mode=dark_mode,
            block_ads=block_ads,
            block_cookie_banners=block_cookie_banners,
        )

        response = self._request("POST", "/v1/screenshot/batch", options.to_dict())
        return BatchResult.from_dict(json.loads(response))

    def get_batch_status(self, job_id: str) -> BatchResult:
        """
        Check the status of a batch job.

        Args:
            job_id: The batch job ID

        Returns:
            BatchResult with status and results if completed
        """
        response = self._request("GET", f"/v1/screenshot/batch/{job_id}")
        return BatchResult.from_dict(json.loads(response))

    def extract(
        self,
        url: str,
        type: ExtractType = "markdown",
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
        """
        Extract content from a web page.

        Args:
            url: URL to extract content from
            type: Extraction type ('markdown', 'text', 'html', 'article',
                  'structured', 'links', 'images', 'metadata')
            selector: CSS selector to scope extraction
            wait_for: CSS selector to wait for before extracting
            timeout: Max wait time in ms
            dark_mode: Emulate dark mode
            block_ads: Block ads
            block_cookie_banners: Hide cookie consent banners
            include_images: Include images in extracted content
            max_length: Maximum content length
            clean_output: Clean and simplify the extracted content

        Returns:
            ExtractResult with extracted content

        Example:
            >>> result = client.extract(
            ...     url='https://example.com',
            ...     type='markdown',
            ...     block_ads=True
            ... )
            >>> print(result.content)
        """
        options = ExtractOptions(
            url=url,
            type=type,
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

        response = self._request("POST", "/v1/extract", options.to_dict())
        return ExtractResult.from_dict(json.loads(response))

    def extract_markdown(self, url: str, **kwargs) -> ExtractResult:
        """
        Extract page content as Markdown.

        Args:
            url: URL to extract content from
            **kwargs: Additional extract options

        Returns:
            ExtractResult with Markdown content
        """
        return self.extract(url=url, type="markdown", **kwargs)

    def extract_article(self, url: str, **kwargs) -> ExtractResult:
        """
        Extract the main article content from a page.

        Args:
            url: URL to extract article from
            **kwargs: Additional extract options

        Returns:
            ExtractResult with article content
        """
        return self.extract(url=url, type="article", **kwargs)

    def extract_structured(self, url: str, **kwargs) -> ExtractResult:
        """
        Extract structured data from a page.

        Args:
            url: URL to extract structured data from
            **kwargs: Additional extract options

        Returns:
            ExtractResult with structured data
        """
        return self.extract(url=url, type="structured", **kwargs)

    def extract_text(self, url: str, **kwargs) -> ExtractResult:
        """
        Extract plain text content from a page.

        Args:
            url: URL to extract text from
            **kwargs: Additional extract options

        Returns:
            ExtractResult with text content
        """
        return self.extract(url=url, type="text", **kwargs)

    def extract_links(self, url: str, **kwargs) -> ExtractResult:
        """
        Extract all links from a page.

        Args:
            url: URL to extract links from
            **kwargs: Additional extract options

        Returns:
            ExtractResult with links
        """
        return self.extract(url=url, type="links", **kwargs)

    def extract_images(self, url: str, **kwargs) -> ExtractResult:
        """
        Extract all images from a page.

        Args:
            url: URL to extract images from
            **kwargs: Additional extract options

        Returns:
            ExtractResult with images
        """
        return self.extract(url=url, type="images", **kwargs)

    def extract_metadata(self, url: str, **kwargs) -> ExtractResult:
        """
        Extract metadata from a page.

        Args:
            url: URL to extract metadata from
            **kwargs: Additional extract options

        Returns:
            ExtractResult with page metadata
        """
        return self.extract(url=url, type="metadata", **kwargs)

    def analyze(
        self,
        url: str,
        prompt: str,
        provider: Optional[AnalyzeProvider] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        wait_for: Optional[str] = None,
        block_ads: bool = False,
        block_cookie_banners: bool = False,
        include_screenshot: Optional[bool] = None,
        include_metadata: Optional[bool] = None,
        max_content_length: Optional[int] = None,
    ) -> AnalyzeResult:
        """
        Analyze a web page using AI.

        Args:
            url: URL to analyze
            prompt: Analysis prompt/question
            provider: AI provider ('openai' or 'anthropic')
            api_key: Provider API key
            model: Model to use (e.g., 'gpt-4o', 'claude-sonnet-4-20250514')
            json_schema: JSON schema for structured output
            timeout: Max wait time in ms
            wait_for: CSS selector to wait for before analyzing
            block_ads: Block ads
            block_cookie_banners: Hide cookie consent banners
            include_screenshot: Include a screenshot in the response
            include_metadata: Include page metadata in the response
            max_content_length: Maximum content length to send to AI

        Returns:
            AnalyzeResult with AI analysis

        Example:
            >>> result = client.analyze(
            ...     url='https://example.com',
            ...     prompt='Summarize the main content of this page',
            ...     provider='openai',
            ...     api_key='sk-...'
            ... )
            >>> print(result.result)
        """
        options = AnalyzeOptions(
            url=url,
            prompt=prompt,
            provider=provider,
            api_key=api_key,
            model=model,
            json_schema=json_schema,
            timeout=timeout,
            wait_for=wait_for,
            block_ads=block_ads,
            block_cookie_banners=block_cookie_banners,
            include_screenshot=include_screenshot,
            include_metadata=include_metadata,
            max_content_length=max_content_length,
        )

        response = self._request("POST", "/v1/analyze", options.to_dict())
        return AnalyzeResult.from_dict(json.loads(response))

    def get_devices(self) -> DevicesResult:
        """
        Get available device presets.

        Returns:
            DevicesResult with device presets grouped by category
        """
        response = self._request("GET", "/v1/devices")
        return DevicesResult.from_dict(json.loads(response))

    def get_capabilities(self) -> CapabilitiesResult:
        """
        Get API capabilities and features.

        Returns:
            CapabilitiesResult with API capabilities
        """
        response = self._request("GET", "/v1/capabilities")
        return CapabilitiesResult.from_dict(json.loads(response))

    def get_usage(self) -> UsageResult:
        """
        Get your API usage statistics.

        Returns:
            UsageResult with usage info (used, limit, remaining, reset_at)
        """
        response = self._request("GET", "/v1/usage")
        return UsageResult.from_dict(json.loads(response))

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{path}"

        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "snapapi-python/1.2.0",
        }

        body = None
        if data:
            body = json.dumps(data).encode("utf-8")

        request = Request(url, data=body, headers=headers, method=method)

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return response.read()
        except HTTPError as e:
            self._handle_http_error(e)
        except URLError as e:
            raise SnapAPIError(
                f"Connection error: {e.reason}",
                code="CONNECTION_ERROR",
                status_code=0,
            )

    def _handle_http_error(self, error: HTTPError) -> None:
        """Parse and raise a SnapAPIError from an HTTP error."""
        try:
            body = json.loads(error.read().decode("utf-8"))
            error_data = body.get("error", {})
            raise SnapAPIError(
                message=error_data.get("message", f"HTTP {error.code}"),
                code=error_data.get("code", "HTTP_ERROR"),
                status_code=error.code,
                details=error_data.get("details"),
            )
        except json.JSONDecodeError:
            raise SnapAPIError(
                message=f"HTTP {error.code}: {error.reason}",
                code="HTTP_ERROR",
                status_code=error.code,
            )
