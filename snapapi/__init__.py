"""
SnapAPI Python SDK
Lightning-fast screenshot API for developers

Usage:
    from snapapi import SnapAPI

    client = SnapAPI(api_key='sk_live_xxx')
    screenshot = client.screenshot(url='https://example.com')
"""

from .client import SnapAPI, SnapAPIError
from .types import (
    ScreenshotOptions,
    ScreenshotResult,
    BatchOptions,
    BatchResult,
    Cookie,
    VideoOptions,
    VideoResult,
    ExtractOptions,
    ExtractResult,
    AnalyzeOptions,
    AnalyzeResult,
)

__version__ = "1.2.0"
__all__ = [
    "SnapAPI",
    "SnapAPIError",
    "ScreenshotOptions",
    "ScreenshotResult",
    "BatchOptions",
    "BatchResult",
    "Cookie",
    "VideoOptions",
    "VideoResult",
    "ExtractOptions",
    "ExtractResult",
    "AnalyzeOptions",
    "AnalyzeResult",
]
