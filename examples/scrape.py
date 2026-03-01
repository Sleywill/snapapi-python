"""examples/scrape.py – SnapAPI v2 Python SDK"""
import os
from snapapi import SnapAPI, ScrapeOptions

client = SnapAPI(api_key=os.environ.get("SNAPAPI_KEY", "sk_live_YOUR_KEY"))


def main():
    # 1. Scrape page text
    result = client.scrape(ScrapeOptions(
        url="https://news.ycombinator.com",
        type="text",
        wait_ms=1000,
        block_resources=True,
    ))
    print("Text (first 500 chars):", result.results[0].data[:500])

    # 2. Scrape links
    links = client.scrape(ScrapeOptions(
        url="https://news.ycombinator.com",
        type="links",
    ))
    print("Links:", links.results[0].data[:500])

    # 3. Multi-page with premium proxy
    multi = client.scrape(ScrapeOptions(
        url="https://news.ycombinator.com",
        type="html",
        pages=3,
        premium_proxy=True,
    ))
    for page in multi.results:
        print(f"Page {page.page} ({page.url}): {len(page.data)} chars")


if __name__ == "__main__":
    main()
