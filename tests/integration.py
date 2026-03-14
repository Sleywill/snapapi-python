#!/usr/bin/env python3
"""
Integration test script for the SnapAPI Python SDK.
Hits the real API — requires a valid API key.

Usage:
    SNAPAPI_KEY=sk_live_... python tests/integration.py
    SNAPAPI_KEY=sk_live_... SNAPAPI_BASE_URL=https://snapapi.pics python tests/integration.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from snapapi import SnapAPI, AsyncSnapAPI, AuthenticationError

API_KEY = os.environ.get("SNAPAPI_KEY", "")
BASE_URL = os.environ.get("SNAPAPI_BASE_URL")

if not API_KEY:
    print("Error: SNAPAPI_KEY environment variable is required", file=sys.stderr)
    sys.exit(1)

passed = 0
failed = 0


def test(name: str):
    """Decorator / context function to record test results."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        global passed, failed
        print(f"  {name} ... ", end="", flush=True)
        try:
            yield
            print("PASS")
            passed += 1
        except Exception as exc:
            print(f"FAIL: {exc}")
            failed += 1

    return _ctx()


def run_sync_tests() -> None:
    snap = SnapAPI(
        api_key=API_KEY,
        **({"base_url": BASE_URL} if BASE_URL else {}),
        timeout=60.0,
    )

    with snap:
        with test("ping()"):
            result = snap.ping()
            assert result.get("status") == "ok", f"Expected 'ok', got {result.get('status')}"

        with test("quota()"):
            usage = snap.quota()
            assert isinstance(usage.used, int), "Expected int"

        with test("screenshot() binary PNG"):
            buf = snap.screenshot(url="https://example.com", format="png")
            assert isinstance(buf, (bytes, bytearray)), "Expected bytes"
            assert len(buf) > 100, "Buffer suspiciously small"

        with test("screenshot() full page JPEG"):
            buf = snap.screenshot(url="https://example.com", full_page=True, format="jpeg", quality=80)
            assert isinstance(buf, (bytes, bytearray))

        with test("pdf()"):
            buf = snap.pdf(url="https://example.com", page_size="a4")
            assert isinstance(buf, (bytes, bytearray))
            assert buf[:4] == b"%PDF", f"Invalid PDF header: {buf[:4]}"

        with test("scrape()"):
            result = snap.scrape(url="https://example.com", type="text")
            assert result.success is True
            assert len(result.results) > 0

        with test("extract()"):
            result = snap.extract(url="https://example.com", type="markdown")
            assert result.success is True
            assert result.content is not None

        with test("og_image()"):
            buf = snap.og_image(url="https://example.com")
            assert isinstance(buf, (bytes, bytearray))

        with test("AuthenticationError on bad key"):
            bad_snap = SnapAPI(api_key="sk_invalid", max_retries=0)
            try:
                bad_snap.screenshot(url="https://example.com")
                raise AssertionError("Expected an error")
            except AuthenticationError:
                pass  # correct
            finally:
                bad_snap.close()


async def run_async_tests() -> None:
    async with AsyncSnapAPI(
        api_key=API_KEY,
        **({"base_url": BASE_URL} if BASE_URL else {}),
        timeout=60.0,
    ) as snap:
        with test("async ping()"):
            result = await snap.ping()
            assert result.get("status") == "ok"

        with test("async screenshot()"):
            buf = await snap.screenshot(url="https://example.com")
            assert isinstance(buf, (bytes, bytearray))

        with test("async scrape()"):
            result = await snap.scrape(url="https://example.com")
            assert result.success is True

        with test("async extract()"):
            result = await snap.extract(url="https://example.com", type="text")
            assert result.success is True

        with test("async quota()"):
            usage = await snap.quota()
            assert isinstance(usage.used, int)


def main() -> None:
    print("\nSnapAPI Python SDK — Integration Tests")
    print("=" * 40)
    print("\nSync client:")
    run_sync_tests()

    print("\nAsync client:")
    asyncio.run(run_async_tests())

    print("\n" + "=" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 40 + "\n")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
