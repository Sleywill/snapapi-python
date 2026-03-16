"""
Internal HTTP helpers -- retry logic, error parsing, shared constants.

This module is an internal implementation detail and is not part of the
public API. It may change without notice.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

from .exceptions import (
    AuthenticationError,
    NetworkError,
    QuotaExceededError,
    RateLimitError,
    SnapAPIError,
    TimeoutError,
    ValidationError,
)

SDK_VERSION = "3.1.0"
DEFAULT_BASE_URL = "https://snapapi.pics"
DEFAULT_TIMEOUT = 60.0  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 0.5  # seconds
MAX_RETRY_DELAY = 30.0  # seconds


def build_headers(api_key: str) -> Dict[str, str]:
    """Build the standard HTTP headers for every request."""
    return {
        "X-Api-Key": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": f"snapapi-python/{SDK_VERSION}",
    }


def parse_error_response(status_code: int, body: bytes, headers: Dict[str, Any]) -> SnapAPIError:
    """Parse an error HTTP response into the appropriate SnapAPI exception."""
    try:
        data: Dict[str, Any] = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        data = {}

    message: str = data.get("message", f"HTTP {status_code}")
    code: Any = data.get("error", "UNKNOWN_ERROR")
    if isinstance(code, dict):
        # Nested error format
        message = code.get("message", message)
        code = code.get("code", "HTTP_ERROR")
    if isinstance(code, str):
        code = code.replace(" ", "_").upper()
    else:
        code = "HTTP_ERROR"
    details = data.get("details")

    if status_code in (401, 403):
        return AuthenticationError(message=message, details=details)

    if status_code == 402:
        if "QUOTA" in code or "quota" in message.lower():
            return QuotaExceededError(message=message, details=details)
        return SnapAPIError(message=message, code=code, status_code=402, details=details)

    if status_code == 422:
        fields: Dict[str, str] = data.get("fields", {})
        return ValidationError(message=message, fields=fields, details=details)

    if status_code == 429:
        retry_after_str = headers.get("retry-after") or headers.get("Retry-After") or ""
        try:
            retry_after = float(retry_after_str)
        except (ValueError, TypeError):
            retry_after = data.get("retryAfter", 1.0)
        return RateLimitError(message=message, retry_after=float(retry_after), details=details)

    return SnapAPIError(message=message, code=code, status_code=status_code, details=details)


def should_retry(error: SnapAPIError) -> bool:
    """Return True if the error warrants an automatic retry."""
    if isinstance(error, RateLimitError):
        return True
    return error.status_code >= 500 or error.status_code == 0


def compute_backoff(attempt: int, base_delay: float) -> float:
    """Exponential backoff, capped at MAX_RETRY_DELAY."""
    delay = base_delay * (2 ** (attempt - 1))
    return min(delay, MAX_RETRY_DELAY)
