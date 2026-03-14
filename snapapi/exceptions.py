"""
Custom exception hierarchy for the SnapAPI Python SDK.

All exceptions extend :class:`SnapAPIError`, which itself extends
:class:`Exception`, so you can catch the base class to handle all
SnapAPI-specific errors in a single ``except`` clause.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class SnapAPIError(Exception):
    """Base exception for all SnapAPI errors.

    Attributes:
        message: Human-readable error description.
        code: Machine-readable error code returned by the API
            (e.g. ``"UNAUTHORIZED"``).
        status_code: HTTP status code. ``0`` when no response was received
            (network error, timeout).
        details: Optional extra detail payload from the API response.
    """

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"code={self.code!r}, status_code={self.status_code})"
        )


class RateLimitError(SnapAPIError):
    """Raised when the API returns HTTP 429 Too Many Requests.

    The SDK retries rate-limited requests automatically (up to ``max_retries``).
    This exception is only raised when all retries are exhausted.

    Attributes:
        retry_after: Seconds to wait before retrying (from ``Retry-After`` header).
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: float = 1.0,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message, code="RATE_LIMITED", status_code=429, details=details)
        self.retry_after = retry_after


class AuthenticationError(SnapAPIError):
    """Raised when the API returns HTTP 401 Unauthorized or 403 Forbidden."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message, code="UNAUTHORIZED", status_code=401, details=details)


class ValidationError(SnapAPIError):
    """Raised when the API returns HTTP 422 Unprocessable Entity.

    Attributes:
        fields: Per-field validation error messages, if provided by the API.
    """

    def __init__(
        self,
        message: str = "Validation error",
        fields: Optional[Dict[str, str]] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message, code="VALIDATION_ERROR", status_code=422, details=details)
        self.fields: Dict[str, str] = fields or {}


class QuotaExceededError(SnapAPIError):
    """Raised when the account has exhausted its API quota (HTTP 402)."""

    def __init__(
        self,
        message: str = "API quota exceeded",
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message, code="QUOTA_EXCEEDED", status_code=402, details=details)


class TimeoutError(SnapAPIError):
    """Raised when a request times out before the API responds."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, code="TIMEOUT", status_code=0)


class NetworkError(SnapAPIError):
    """Raised when a network-level failure prevents a response (DNS, connection refused, etc.)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="NETWORK_ERROR", status_code=0)
