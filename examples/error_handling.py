"""
Error handling example demonstrating all error types.

Usage:
    SNAPAPI_KEY=sk_live_... python examples/error_handling.py
"""

import os

from snapapi import (
    AsyncSnapAPI,
    AuthenticationError,
    NetworkError,
    QuotaExceededError,
    RateLimitError,
    SnapAPI,
    SnapAPIError,
    TimeoutError,
    ValidationError,
)

with SnapAPI(api_key=os.environ["SNAPAPI_KEY"]) as snap:
    try:
        data = snap.screenshot(url="https://example.com")
        print(f"Screenshot captured: {len(data)} bytes")
    except AuthenticationError:
        print("Invalid API key. Get yours at https://snapapi.pics")
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after}s")
    except QuotaExceededError:
        print("Quota exceeded. Upgrade at https://snapapi.pics/pricing")
    except ValidationError as e:
        print(f"Invalid options: {e.fields}")
    except TimeoutError:
        print("Request timed out -- try increasing the timeout")
    except NetworkError as e:
        print(f"Network error: {e}")
    except SnapAPIError as e:
        print(f"API error [{e.code}] HTTP {e.status_code}: {e.message}")
