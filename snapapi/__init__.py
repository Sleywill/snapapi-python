"""
SnapAPI Python SDK v3.0.0

Lightning-fast screenshot, scrape, extract, PDF, video, and AI-analyze API.

Sync usage::

    from snapapi import SnapAPI

    with SnapAPI(api_key="sk_live_...") as snap:
        buf = snap.screenshot(url="https://example.com")
        with open("shot.png", "wb") as f:
            f.write(buf)

Async usage::

    import asyncio
    from snapapi import AsyncSnapAPI

    async def main():
        async with AsyncSnapAPI(api_key="sk_live_...") as snap:
            buf = await snap.screenshot(url="https://example.com")
            with open("shot.png", "wb") as f:
                f.write(buf)

    asyncio.run(main())
"""

from .client import SnapAPI
from .async_client import AsyncSnapAPI
from .exceptions import (
    SnapAPIError,
    RateLimitError,
    AuthenticationError,
    ValidationError,
    QuotaExceededError,
    TimeoutError,
    NetworkError,
)
from .types import (
    # Core
    ScreenshotOptions,
    ScreenshotResult,
    Cookie,
    HttpAuth,
    ProxyConfig,
    Geolocation,
    PdfOptions,
    ThumbnailOptions,
    ExtractMetadata,
    DevicePreset,
    # Video
    VideoOptions,
    VideoResult,
    ScrollEasing,
    # Batch (legacy)
    BatchOptions,
    BatchResult,
    # Scrape
    ScrapeOptions,
    ScrapeResult,
    ScrapePageResult,
    # Extract
    ExtractOptions,
    ExtractResult,
    ExtractType,
    # Analyze
    AnalyzeOptions,
    AnalyzeResult,
    AnalyzeProvider,
    # Usage
    UsageResult,
    # Storage (v2)
    StorageFile,
    StorageListResult,
    StorageUsage,
    S3Config,
    S3TestResult,
    DeleteResult,
    # Scheduled (v2)
    CreateScheduledOptions,
    ScheduledScreenshot,
    # Webhooks (v2)
    CreateWebhookOptions,
    Webhook,
    # API Keys (v2)
    ApiKey,
    CreateApiKeyResult,
)

__version__ = "3.0.0"

__all__ = [
    # Clients
    "SnapAPI",
    "AsyncSnapAPI",
    # Exceptions
    "SnapAPIError",
    "RateLimitError",
    "AuthenticationError",
    "ValidationError",
    "QuotaExceededError",
    "TimeoutError",
    "NetworkError",
    # Core types
    "ScreenshotOptions",
    "ScreenshotResult",
    "Cookie",
    "HttpAuth",
    "ProxyConfig",
    "Geolocation",
    "PdfOptions",
    "ThumbnailOptions",
    "ExtractMetadata",
    "DevicePreset",
    # Video
    "VideoOptions",
    "VideoResult",
    "ScrollEasing",
    # Batch (legacy)
    "BatchOptions",
    "BatchResult",
    # Scrape
    "ScrapeOptions",
    "ScrapeResult",
    "ScrapePageResult",
    # Extract
    "ExtractOptions",
    "ExtractResult",
    "ExtractType",
    # Analyze
    "AnalyzeOptions",
    "AnalyzeResult",
    "AnalyzeProvider",
    # Usage
    "UsageResult",
    # Storage (v2)
    "StorageFile",
    "StorageListResult",
    "StorageUsage",
    "S3Config",
    "S3TestResult",
    "DeleteResult",
    # Scheduled (v2)
    "CreateScheduledOptions",
    "ScheduledScreenshot",
    # Webhooks (v2)
    "CreateWebhookOptions",
    "Webhook",
    # API Keys (v2)
    "ApiKey",
    "CreateApiKeyResult",
]
