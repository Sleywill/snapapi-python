# SnapAPI Python SDK

Official Python SDK for [SnapAPI](https://snapapi.pics) — the lightning-fast screenshot, scrape, extract, PDF, video, and AI-analyze API.

## Installation

```bash
pip install snapapi
```

## Quick Start

```python
from snapapi import SnapAPI

with SnapAPI(api_key="sk_live_...") as snap:
    # Take a screenshot
    data = snap.screenshot(url="https://example.com")
    with open("screenshot.png", "wb") as f:
        f.write(data)

    # Or save directly to a file
    snap.screenshot_to_file("https://example.com", "./screenshot.png")
```

### Async Usage

```python
import asyncio
from snapapi import AsyncSnapAPI

async def main():
    async with AsyncSnapAPI(api_key="sk_live_...") as snap:
        data = await snap.screenshot(url="https://example.com")
        with open("screenshot.png", "wb") as f:
            f.write(data)

asyncio.run(main())
```

## Features

- **Both sync and async clients** — `SnapAPI` and `AsyncSnapAPI`
- **Full type hints** on every method and response
- **Dataclass response types** — structured, IDE-friendly responses
- **Automatic retries** with exponential backoff on 429 / 5xx
- **Rate limit handling** with `Retry-After` header support
- **Context manager support** — automatic connection cleanup
- **All endpoints** — screenshot, scrape, extract, PDF, video, OG image, analyze
- **Sub-namespaces** — storage, scheduled jobs, webhooks, API key management
- **Custom typed exceptions** per error category
- Python 3.8+

## Configuration

```python
snap = SnapAPI(
    api_key="sk_live_...",
    base_url="https://api.snapapi.pics",  # Default
    timeout=60.0,                          # 60s default
    max_retries=3,                         # Auto-retry on 429 / 5xx
    retry_delay=0.5,                       # Initial backoff (doubles each retry)
)
```

## API Reference

### Screenshot

Capture a screenshot of any URL, raw HTML, or Markdown.

```python
# Basic PNG screenshot
data = snap.screenshot(url="https://example.com")

# Full-page dark-mode WebP with ad blocking
data = snap.screenshot(
    url="https://github.com",
    format="webp",
    full_page=True,
    dark_mode=True,
    block_ads=True,
    block_cookie_banners=True,
)

# Custom viewport (mobile)
data = snap.screenshot(
    url="https://example.com",
    device="iphone-15-pro",
)

# From raw HTML
data = snap.screenshot(
    html='<h1 style="color: red;">Hello World</h1>',
    width=800,
    height=600,
)

# Store in SnapAPI cloud (returns URL instead of binary)
result = snap.screenshot_to_storage(url="https://example.com")
print(result.url)  # Public URL

# Save directly to file
snap.screenshot_to_file("https://example.com", "./output/shot.png")
snap.screenshot_to_file(
    "https://example.com",
    "./output/full.webp",
    format="webp",
    full_page=True,
)
```

**Key screenshot options:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | URL to capture |
| `html` | `str` | — | Raw HTML to render |
| `markdown` | `str` | — | Markdown to render |
| `format` | `str` | `'png'` | `png`, `jpeg`, `webp`, `avif`, `pdf` |
| `quality` | `int` | — | JPEG/WebP quality 1–100 |
| `device` | `str` | — | Named device preset |
| `width` | `int` | `1280` | Viewport width |
| `height` | `int` | `800` | Viewport height |
| `full_page` | `bool` | `False` | Capture full scrollable page |
| `selector` | `str` | — | CSS selector to capture |
| `delay` | `int` | `0` | Delay before capture (ms) |
| `wait_until` | `str` | — | `load`, `domcontentloaded`, `networkidle` |
| `dark_mode` | `bool` | `False` | Dark color scheme |
| `css` | `str` | — | Custom CSS to inject |
| `javascript` | `str` | — | JS to execute before capture |
| `block_ads` | `bool` | `False` | Block ad networks |
| `block_cookie_banners` | `bool` | `False` | Block consent popups |
| `user_agent` | `str` | — | Custom User-Agent |
| `extra_headers` | `dict` | — | Extra HTTP headers |
| `cookies` | `list` | — | Cookies to inject |
| `proxy` | `dict` | — | Custom proxy config |
| `premium_proxy` | `bool` | — | Use SnapAPI rotating proxy |

### Scrape

Scrape text, HTML, or links from web pages using a stealth browser.

```python
result = snap.scrape(
    url="https://news.ycombinator.com",
    type="links",
    pages=3,
    block_resources=True,
)

for page in result.results:
    print(f"Page {page.page}: {page.data[:100]}...")
```

### Extract

Extract structured content — markdown, text, article, links, images, or metadata.

```python
result = snap.extract(
    url="https://example.com/blog/post",
    type="markdown",
    clean_output=True,
    include_images=False,
)

print(result.data)  # Clean markdown content
```

Extract convenience methods:

```python
result = snap.extract_markdown("https://example.com")
result = snap.extract_article("https://example.com/post")
result = snap.extract_text("https://example.com")
result = snap.extract_links("https://example.com")
result = snap.extract_images("https://example.com")
result = snap.extract_metadata("https://example.com")
```

### PDF

Convert URLs or HTML to PDF documents.

```python
# From URL
pdf_data = snap.pdf(
    url="https://example.com/invoice",
    page_size="a4",
    margin_top="20mm",
    margin_bottom="20mm",
)
with open("invoice.pdf", "wb") as f:
    f.write(pdf_data)

# From HTML
pdf_data = snap.pdf(
    html="<h1>Invoice #1234</h1><p>Total: $99.00</p>",
    landscape=True,
)

# Save directly to file
snap.pdf_to_file("https://example.com", "./output.pdf")
```

### Video

Record a video of a live webpage.

```python
video_data = snap.video(
    url="https://example.com",
    format="mp4",
    duration=10,
    scrolling=True,
    scroll_speed=200,
)
with open("recording.mp4", "wb") as f:
    f.write(video_data)
```

### OG Image

Generate Open Graph social images.

```python
og_data = snap.og_image(
    url="https://example.com",
    format="png",
    width=1200,
    height=630,
)
with open("og.png", "wb") as f:
    f.write(og_data)
```

### Analyze (AI)

Analyze webpages with an LLM — bring your own API key.

```python
result = snap.analyze(
    url="https://example.com/pricing",
    prompt="Extract all pricing tiers as JSON with name, price, and features.",
    provider="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    json_schema={
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "price": {"type": "string"},
                "features": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
)
print(result.analysis)
```

### Usage / Quota

```python
usage = snap.get_usage()
print(f"{usage.used} / {usage.limit} API calls used (resets {usage.reset_at})")
```

### Ping

```python
result = snap.ping()
# PingResult(status='ok', timestamp=1710540000000)
```

## Sub-Namespaces

### Storage

```python
# List stored files
response = snap.storage.list_files(limit=50, offset=0)
for f in response.files:
    print(f.id, f.url)

# Get a specific file
file = snap.storage.get_file("file_abc")

# Delete a file
snap.storage.delete_file("file_abc")

# Get storage usage
usage = snap.storage.get_usage()

# Configure custom S3
snap.storage.configure_s3(
    s3_bucket="my-bucket",
    s3_region="us-east-1",
    s3_access_key_id="...",
    s3_secret_access_key="...",
)
```

### Scheduled Screenshots

```python
# Create a scheduled job (runs daily at 9am)
job = snap.scheduled.create(
    url="https://example.com",
    cron_expression="0 9 * * *",
    format="png",
    webhook_url="https://my-app.com/webhook",
)

# List all jobs
jobs = snap.scheduled.list()

# Delete a job
snap.scheduled.delete(job.id)
```

### Webhooks

```python
wh = snap.webhooks.create(
    url="https://my-app.com/hooks/snapapi",
    events=["screenshot.done"],
    secret="my-signing-secret",
)

all_wh = snap.webhooks.list()
snap.webhooks.delete(wh.id)
```

### API Keys

```python
new_key = snap.keys.create("production")
print(new_key.key)  # Full key — store securely!

all_keys = snap.keys.list()
snap.keys.delete("key_id")
```

## Error Handling

All exceptions extend `SnapAPIError` with `code`, `status_code`, and `message` fields.

```python
from snapapi import (
    SnapAPIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    QuotaExceededError,
    TimeoutError,
    NetworkError,
)

try:
    data = snap.screenshot(url="https://example.com")
except AuthenticationError:
    print("Invalid API key. Get yours at https://snapapi.pics")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except QuotaExceededError:
    print("Quota exceeded. Upgrade at https://snapapi.pics/pricing")
except ValidationError as e:
    print(f"Invalid options: {e.fields}")
except TimeoutError:
    print("Request timed out")
except NetworkError as e:
    print(f"Network error: {e}")
except SnapAPIError as e:
    print(f"API error [{e.code}]: {e.message}")
```

## Advanced Usage

### Proxies

```python
# Custom proxy
data = snap.screenshot(
    url="https://example.com",
    proxy={"server": "http://proxy.example.com:8080", "username": "user", "password": "pass"},
)

# SnapAPI built-in rotating proxy
data = snap.screenshot(url="https://example.com", premium_proxy=True)
```

### Custom Headers and Cookies

```python
data = snap.screenshot(
    url="https://app.example.com/dashboard",
    extra_headers={"Accept-Language": "fr-FR"},
    cookies=[
        {
            "name": "session",
            "value": "abc123",
            "domain": "app.example.com",
            "secure": True,
            "http_only": True,
        }
    ],
)
```

### Batch Processing

```python
import asyncio
from snapapi import AsyncSnapAPI

async def batch_screenshots(urls: list[str]):
    async with AsyncSnapAPI(api_key="sk_live_...") as snap:
        tasks = [snap.screenshot(url=url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            print(f"FAIL: {url} — {result}")
        else:
            print(f"OK:   {url} — {len(result)} bytes")

asyncio.run(batch_screenshots([
    "https://example.com",
    "https://github.com",
    "https://python.org",
]))
```

### LLM Data Pipeline

```python
# Extract page content
content = snap.extract(
    url="https://example.com/article",
    type="markdown",
    clean_output=True,
)

# Then analyze with AI
analysis = snap.analyze(
    url="https://example.com/article",
    prompt="Summarize the key points and sentiment.",
    provider="openai",
    api_key=os.environ["OPENAI_API_KEY"],
)

print(analysis.analysis)
```

### Visual Regression Testing

```python
import hashlib

def check_for_changes(url: str, previous_hash: str) -> str:
    data = snap.screenshot(url=url, full_page=True)
    current_hash = hashlib.sha256(data).hexdigest()

    if current_hash != previous_hash:
        print(f"Page changed: {url}")
    return current_hash
```

## Requirements

- Python 3.8+
- `httpx >= 0.24.0`

## License

MIT — see [LICENSE](./LICENSE).

## Links

- [SnapAPI Website](https://snapapi.pics)
- [API Documentation](https://snapapi.pics/docs)
- [GitHub Issues](https://github.com/Sleywill/snapapi-python/issues)
- [Changelog](./CHANGELOG.md)
