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
    Cookie,
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

    DEFAULT_BASE_URL = "https://api.snapapi.dev"
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
        url: str,
        format: str = "png",
        width: int = 1920,
        height: int = 1080,
        full_page: bool = False,
        quality: Optional[int] = None,
        scale: float = 1.0,
        delay: int = 0,
        timeout: int = 30000,
        dark_mode: bool = False,
        mobile: bool = False,
        selector: Optional[str] = None,
        wait_for_selector: Optional[str] = None,
        javascript: Optional[str] = None,
        block_ads: bool = False,
        hide_cookie_banners: bool = False,
        cookies: Optional[List[Cookie]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_type: str = "binary",
    ) -> Union[bytes, ScreenshotResult]:
        """
        Capture a screenshot of the specified URL.

        Args:
            url: URL to capture
            format: Output format ('png', 'jpeg', 'webp', 'pdf')
            width: Viewport width (100-3840)
            height: Viewport height (100-2160)
            full_page: Capture full scrollable page
            quality: Image quality 1-100 (JPEG/WebP only)
            scale: Device scale factor 0.5-3
            delay: Delay before capture in ms (0-10000)
            timeout: Max wait time in ms (1000-60000)
            dark_mode: Emulate dark mode
            mobile: Emulate mobile device
            selector: CSS selector for element capture
            wait_for_selector: Wait for element before capture
            javascript: JS to execute before capture
            block_ads: Block ads and trackers
            hide_cookie_banners: Hide cookie consent banners
            cookies: Cookies to set
            headers: Custom HTTP headers
            response_type: 'binary', 'base64', or 'json'

        Returns:
            bytes if response_type is 'binary', ScreenshotResult otherwise

        Example:
            >>> screenshot = client.screenshot(
            ...     url='https://example.com',
            ...     format='png',
            ...     full_page=True,
            ...     dark_mode=True
            ... )
            >>> with open('screenshot.png', 'wb') as f:
            ...     f.write(screenshot)
        """
        options = ScreenshotOptions(
            url=url,
            format=format,
            width=width,
            height=height,
            full_page=full_page,
            quality=quality,
            scale=scale,
            delay=delay,
            timeout=timeout,
            dark_mode=dark_mode,
            mobile=mobile,
            selector=selector,
            wait_for_selector=wait_for_selector,
            javascript=javascript,
            block_ads=block_ads,
            hide_cookie_banners=hide_cookie_banners,
            cookies=cookies,
            headers=headers,
            response_type=response_type,
        )

        response = self._request("POST", "/v1/screenshot", options.to_dict())

        if response_type == "binary":
            return response
        elif response_type == "json":
            return ScreenshotResult.from_dict(json.loads(response))
        else:
            return response

    def batch(
        self,
        urls: List[str],
        format: str = "png",
        width: int = 1920,
        height: int = 1080,
        full_page: bool = False,
        webhook_url: Optional[str] = None,
        dark_mode: bool = False,
        block_ads: bool = False,
    ) -> BatchResult:
        """
        Capture screenshots of multiple URLs.

        Args:
            urls: List of URLs to capture
            format: Output format
            width: Viewport width
            height: Viewport height
            full_page: Capture full page
            webhook_url: URL for async notifications
            dark_mode: Emulate dark mode
            block_ads: Block ads

        Returns:
            BatchResult with job ID and status

        Example:
            >>> batch = client.batch(
            ...     urls=['https://example.com', 'https://example.org'],
            ...     webhook_url='https://your-server.com/webhook'
            ... )
            >>> print(batch.job_id)
        """
        options = BatchOptions(
            urls=urls,
            format=format,
            width=width,
            height=height,
            full_page=full_page,
            webhook_url=webhook_url,
            dark_mode=dark_mode,
            block_ads=block_ads,
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

    def get_usage(self) -> Dict[str, Any]:
        """
        Get your API usage statistics.

        Returns:
            Dictionary with usage info (used, limit, remaining, reset_at)
        """
        response = self._request("GET", "/v1/usage")
        return json.loads(response)

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
            "User-Agent": "snapapi-python/1.0.0",
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
