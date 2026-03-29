"""
Async batch processing example -- capture multiple URLs concurrently.

Usage:
    SNAPAPI_KEY=sk_live_... python examples/async_batch.py
"""

import asyncio
import os

from snapapi import AsyncSnapAPI

URLS = [
    "https://example.com",
    "https://github.com",
    "https://python.org",
    "https://docs.python.org",
]


async def main() -> None:
    async with AsyncSnapAPI(api_key=os.environ["SNAPAPI_KEY"]) as snap:
        print(f"Capturing {len(URLS)} screenshots concurrently...")

        tasks = [snap.screenshot(url=url) for url in URLS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for url, result in zip(URLS, results):
            if isinstance(result, Exception):
                print(f"FAIL: {url} -- {result}")
            else:
                assert isinstance(result, bytes)
                print(f"OK:   {url} -- {len(result)} bytes")


asyncio.run(main())
