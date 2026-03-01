"""
SnapAPI Python SDK v2.0.0
Lightning-fast screenshot, scrape, extract, and AI-analyze API for developers.

Usage::

    from snapapi import SnapAPI

    client = SnapAPI(api_key='sk_live_xxx')
    screenshot = client.screenshot(url='https://example.com')
    with open('shot.png', 'wb') as f:
        f.write(screenshot)

Async usage::

    import asyncio
    from snapapi import AsyncSnapAPI

    async def main():
        async with AsyncSnapAPI(api_key='sk_live_xxx') as client:
            buf = await client.screenshot(url='https://example.com')

    asyncio.run(main())
"""

from .client import SnapAPI, SnapAPIError

try:
    from .async_client import AsyncSnapAPI
except ImportError:
    AsyncSnapAPI = None  # type: ignore[assignment,misc]
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
    # Video / Batch (legacy)
    VideoOptions,
    VideoResult,
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

__version__ = "2.0.0"

__all__ = [
    # Clients
    "SnapAPI",
    "AsyncSnapAPI",
    "SnapAPIError",
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
    # Video / Batch
    "VideoOptions",
    "VideoResult",
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
