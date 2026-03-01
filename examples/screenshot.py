"""examples/screenshot.py – SnapAPI v2 Python SDK"""
import os
from snapapi import SnapAPI

client = SnapAPI(api_key=os.environ.get("SNAPAPI_KEY", "sk_live_YOUR_KEY"))


def main():
    # 1. Basic PNG screenshot
    print("Taking basic screenshot…")
    buf = client.screenshot(url="https://example.com")
    open("basic.png", "wb").write(buf)
    print("Saved basic.png")

    # 2. Full-page dark-mode WebP
    buf2 = client.screenshot(
        url="https://example.com",
        format="webp",
        full_page=True,
        dark_mode=True,
        block_ads=True,
        block_cookie_banners=True,
        quality=80,
    )
    open("dark-full.webp", "wb").write(buf2)
    print("Saved dark-full.webp")

    # 3. Mobile device preset
    buf3 = client.screenshot(
        url="https://example.com",
        device="iphone-15-pro",
        format="png",
    )
    open("mobile.png", "wb").write(buf3)
    print("Saved mobile.png")

    # 4. Render HTML
    buf4 = client.screenshot(
        html="""<!DOCTYPE html><html><body style="background:#1a1a2e;color:#e0e0e0;
        font-family:sans-serif;padding:40px"><h1>Hello from SnapAPI!</h1></body></html>""",
        width=800,
        height=300,
        format="png",
    )
    open("html.png", "wb").write(buf4)
    print("Saved html.png")

    # 5. PDF generation
    pdf = client.screenshot(
        url="https://example.com",
        format="pdf",
        page_size="a4",
        margins={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"},
    )
    open("page.pdf", "wb").write(pdf)
    print("Saved page.pdf")

    # 6. Store in SnapAPI cloud
    stored = client.screenshot(
        url="https://example.com",
        storage={"destination": "snapapi"},
    )
    print("Stored file URL:", stored.get("url"), "ID:", stored.get("id"))

    # 7. Async via webhook
    queued = client.screenshot(
        url="https://example.com",
        webhook_url="https://webhook.site/your-id",
    )
    print("Queued job ID:", queued.get("jobId"))


if __name__ == "__main__":
    main()
