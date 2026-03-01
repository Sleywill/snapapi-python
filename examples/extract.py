"""examples/extract.py – SnapAPI v2 Python SDK"""
import os
from snapapi import SnapAPI, ExtractOptions

client = SnapAPI(api_key=os.environ.get("SNAPAPI_KEY", "sk_live_YOUR_KEY"))
URL = "https://en.wikipedia.org/wiki/Screenshot"


def main():
    # 1. Markdown (great for LLM context)
    md = client.extract(ExtractOptions(
        url=URL, type="markdown", clean_output=True, max_length=3000
    ))
    print("Markdown (first 500):", str(md.content)[:500])
    print("Response time:", md.took, "ms")

    # 2. Article body
    article = client.extract(ExtractOptions(url=URL, type="article"))
    print("Article length:", len(str(article.content)))

    # 3. Links
    links = client.extract(ExtractOptions(url=URL, type="links"))
    print("Links:", links.content)

    # 4. Images
    images = client.extract(ExtractOptions(url=URL, type="images"))
    print("Images:", images.content)

    # 5. Metadata
    meta = client.extract(ExtractOptions(url=URL, type="metadata"))
    print("Metadata:", meta.content)

    # 6. Structured data (JSON-LD / microdata)
    structured = client.extract(ExtractOptions(url=URL, type="structured"))
    print("Structured:", structured.content)


if __name__ == "__main__":
    main()
