"""
Basic screenshot example.

Usage:
    SNAPAPI_KEY=sk_live_... python examples/basic_screenshot.py
"""

import os

from snapapi import SnapAPI

with SnapAPI(api_key=os.environ["SNAPAPI_KEY"]) as snap:
    # Take a simple PNG screenshot
    data = snap.screenshot(url="https://example.com")
    with open("screenshot.png", "wb") as f:
        f.write(data)
    print(f"Saved screenshot.png ({len(data)} bytes)")

    # Full-page dark-mode WebP with ad blocking
    full_page = snap.screenshot(
        url="https://github.com",
        format="webp",
        full_page=True,
        dark_mode=True,
        block_ads=True,
        block_cookie_banners=True,
        quality=80,
    )
    with open("full-page.webp", "wb") as f:
        f.write(full_page)
    print(f"Saved full-page.webp ({len(full_page)} bytes)")

    # Save directly to file (convenience method)
    snap.screenshot_to_file("https://nodejs.org", "./nodejs.png")
    print("Saved nodejs.png")
