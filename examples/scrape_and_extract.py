"""
Web scraping and content extraction example.

Usage:
    SNAPAPI_KEY=sk_live_... python examples/scrape_and_extract.py
"""

import os

from snapapi import SnapAPI

with SnapAPI(api_key=os.environ["SNAPAPI_KEY"]) as snap:
    # Scrape links from Hacker News
    result = snap.scrape(
        url="https://news.ycombinator.com",
        type="links",
        pages=2,
        block_resources=True,
    )
    for page in result.results:
        print(f"Page {page.page}: {page.data[:100]}...")

    print()

    # Extract clean markdown
    extract_result = snap.extract(
        url="https://example.com",
        type="markdown",
        clean_output=True,
        max_length=5000,
    )
    print("Extracted content:")
    print(extract_result.content)

    # Use convenience methods
    md = snap.extract_markdown("https://example.com")
    print(f"\nMarkdown: {str(md.content)[:100]}...")

    links = snap.extract_links("https://example.com")
    print(f"Links: {links.content}")
