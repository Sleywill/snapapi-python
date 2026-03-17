# SnapAPI Python SDK

Official Python SDK for [SnapAPI](https://snapapi.pics) — the lightning-fast screenshot, scrape, extract, PDF, video, and AI-analyze API.

[![PyPI version](https://img.shields.io/pypi/v/snapapi-client?label=pypi&color=3776ab)](https://pypi.org/project/snapapi-client/)
[![CI](https://github.com/Sleywill/snapapi-python/actions/workflows/ci.yml/badge.svg)](https://github.com/Sleywill/snapapi-python/actions)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## Installation

```bash
pip install snapapi-client
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
- **Storage, scheduled jobs, webhooks, API key management**
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

# Store in SnapAPI cloud — returns a dict with a public URL
result = snap.screenshot_to_storage("https://example.com")
print(result["url"])  # Public CDN URL

# Store in your own S3
result = snap.screenshot_to_storage("https://example.com", destination="user_s3")

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
| `device` | `str` | — | Named device preset (e.g. `'iphone-15-pro'`) |
| `width` | `int` | `1280` | Viewport width |
| `height` | `int` | `800` | Viewport height |
| `device_scale_factor` | `float` | `1.0` | Device pixel ratio 1–3 |
| `full_page` | `bool` | `False` | Capture full scrollable page |
| `selector` | `str` | — | CSS selector to capture |
| `delay` | `int` | `0` | Delay before capture (ms) |
| `timeout` | `int` | — | Navigation timeout (ms) |
| `wait_until` | `str` | — | `load`, `domcontentloaded`, `networkidle` |
| `wait_for_selector` | `str` | — | Wait for this CSS selector to appear |
| `dark_mode` | `bool` | `False` | Dark color scheme |
| `reduced_motion` | `bool` | `False` | Reduce CSS animations |
| `css` | `str` | — | Custom CSS to inject |
| `javascript` | `str` | — | JS to execute before capture |
| `hide_selectors` | `list` | — | CSS selectors to hide |
| `click_selector` | `str` | — | Click this element before capture |
| `block_ads` | `bool` | `False` | Block ad networks |
| `block_trackers` | `bool` | `False` | Block tracking scripts |
| `block_cookie_banners` | `bool` | `False` | Block consent popups |
| `block_chat_widgets` | `bool` | `False` | Block chat widgets |
| `user_agent` | `str` | — | Custom User-Agent |
| `extra_headers` | `dict` | — | Extra HTTP headers |
| `cookies` | `list` | — | Cookies to inject |
| `http_auth` | `HttpAuth` | — | HTTP Basic Auth credentials |
| `proxy` | `ProxyConfig` | — | Custom proxy config |
| `premium_proxy` | `bool` | — | Use SnapAPI rotating proxy |
| `geolocation` | `Geolocation` | — | GPS coordinates to emulate |
| `timezone` | `str` | — | IANA timezone string |
| `cache` | `bool` | `False` | Cache the result |
| `cache_ttl` | `int` | — | Cache TTL in seconds |

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

**Scrape options:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | URL to scrape (required) |
| `type` | `str` | `'text'` | `text`, `html`, `links` |
| `pages` | `int` | `1` | Number of pages to scrape (1–10) |
| `wait_ms` | `int` | — | Wait after page load (ms) |
| `proxy` | `str` | — | Proxy URL |
| `premium_proxy` | `bool` | — | Use SnapAPI rotating proxy |
| `block_resources` | `bool` | `False` | Block images/fonts/media |
| `locale` | `str` | — | Browser locale |

### Extract

Extract structured content — markdown, text, article, links, images, or metadata.

```python
result = snap.extract(
    url="https://example.com/blog/post",
    type="markdown",
    clean_output=True,
    include_images=False,
)

print(result.content)  # Clean markdown content
```

Extract convenience methods — shortcuts that set the `type` parameter for you:

```python
result = snap.extract_markdown("https://example.com")
result = snap.extract_article("https://example.com/post")
result = snap.extract_text("https://example.com")
result = snap.extract_links("https://example.com")
result = snap.extract_images("https://example.com")
result = snap.extract_metadata("https://example.com")

print(result.content)  # Content in the type appropriate format
```

**Extract options:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | URL to extract from (required) |
| `type` | `str` | `'markdown'` | `markdown`, `text`, `html`, `article`, `links`, `images`, `metadata`, `structured` |
| `selector` | `str` | — | CSS selector to scope extraction |
| `wait_for` | `str` | — | Wait for CSS selector before extracting |
| `timeout` | `int` | — | Navigation timeout (ms) |
| `include_images` | `bool` | — | Include image URLs in output |
| `max_length` | `int` | — | Truncate output at N characters |
| `clean_output` | `bool` | — | Strip navigation and boilerplate |
| `block_ads` | `bool` | `False` | Block ad networks |
| `block_cookie_banners` | `bool` | `False` | Block consent popups |

### PDF

Convert URLs or HTML to PDF documents.

```python
# From URL with custom margins
pdf_data = snap.pdf(
    url="https://example.com/invoice",
    page_size="a4",
    margins={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"},
)
with open("invoice.pdf", "wb") as f:
    f.write(pdf_data)

# From HTML
pdf_data = snap.pdf(
    html="<h1>Invoice #1234</h1><p>Total: $99.00</p>",
    landscape=True,
)

# Save directly to file
snap.pdf_to_file("https://example.com", "./output.pdf", page_size="letter")
```

**PDF options:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | URL to convert |
| `html` | `str` | — | HTML string to convert |
| `page_size` | `str` | `'a4'` | `a4`, `a3`, `a5`, `letter`, `legal`, `tabloid` |
| `landscape` | `bool` | `False` | Landscape orientation |
| `margins` | `dict` | — | Page margins: `{'top': '20mm', 'right': '15mm', 'bottom': '20mm', 'left': '15mm'}` |
| `header_template` | `str` | — | HTML template for page header |
| `footer_template` | `str` | — | HTML template for page footer |
| `display_header_footer` | `bool` | `False` | Show header and footer |
| `scale` | `float` | — | Content scale factor 0.1–2 |
| `delay` | `int` | `0` | Extra delay before rendering (ms) |
| `wait_for_selector` | `str` | — | Wait for CSS selector before rendering |

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

**Video options:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | URL to record (required) |
| `format` | `str` | `'mp4'` | `mp4`, `webm`, `gif` |
| `width` | `int` | `1280` | Viewport width |
| `height` | `int` | `720` | Viewport height |
| `duration` | `int` | `5` | Duration in seconds (1–30) |
| `fps` | `int` | `25` | Frames per second (10–30) |
| `scrolling` | `bool` | `False` | Enable scroll animation |
| `scroll_speed` | `int` | — | Scroll speed px/s (50–500) |
| `scroll_delay` | `int` | — | Delay before scroll starts (ms) |
| `dark_mode` | `bool` | `False` | Enable dark mode |
| `block_ads` | `bool` | `False` | Block ad networks |
| `delay` | `int` | `0` | Delay before recording starts (ms) |

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
import os

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
print(result.result)  # AI-generated analysis
```

**Analyze options:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | — | URL to analyze (required) |
| `prompt` | `str` | — | Analysis prompt (required) |
| `provider` | `str` | — | `openai` or `anthropic` |
| `api_key` | `str` | — | Your LLM provider API key |
| `model` | `str` | — | Override default model |
| `json_schema` | `dict` | — | JSON schema for structured output |
| `include_screenshot` | `bool` | — | Include screenshot in analysis context |
| `include_metadata` | `bool` | — | Include page metadata in context |
| `max_content_length` | `int` | — | Max characters of page content to send |

### Usage / Quota

```python
usage = snap.get_usage()
print(f"{usage.used} / {usage.limit} API calls used (resets {usage.reset_at})")

# Alias
usage = snap.quota()
```

### Ping

```python
result = snap.ping()
# {'status': 'ok', 'timestamp': 1710540000000}
```

## Storage

```python
from snapapi import S3Config

# List stored files
response = snap.storage_list_files(limit=50, offset=0)
for f in response.files:
    print(f.id, f.url)

# Get a specific file
file = snap.storage_get_file("file_abc")
print(file.url, file.size)

# Delete a file
result = snap.storage_delete_file("file_abc")

# Get storage usage
usage = snap.storage_get_usage()
print(f"{usage.used_formatted} of {usage.limit_formatted} used")

# Configure custom S3
config = S3Config(
    s3_bucket="my-bucket",
    s3_region="us-east-1",
    s3_access_key_id="AKID...",
    s3_secret_access_key="secret...",
    s3_endpoint="https://s3.example.com",  # optional, for S3-compatible providers
)
snap.storage_configure_s3(config)

# Test S3 connection
result = snap.storage_test_s3()
print(result.success, result.message)
```

## Scheduled Screenshots

```python
from snapapi import CreateScheduledOptions

# Create a scheduled job (runs daily at 9am UTC)
options = CreateScheduledOptions(
    url="https://example.com",
    cron_expression="0 9 * * *",
    format="png",
    webhook_url="https://my-app.com/webhook",
)
job = snap.scheduled_create(options)
print(job.id, job.next_run)

# List all jobs
jobs = snap.scheduled_list()

# Delete a job
result = snap.scheduled_delete(job.id)
```

## Webhooks

```python
from snapapi import CreateWebhookOptions

options = CreateWebhookOptions(
    url="https://my-app.com/hooks/snapapi",
    events=["screenshot.done"],
    secret="my-signing-secret",
)
wh = snap.webhooks_create(options)
print(wh.id)

all_wh = snap.webhooks_list()
result = snap.webhooks_delete(wh.id)
```

## API Keys

```python
# Create a new key (full key returned only once — store it securely)
new_key = snap.keys_create("production")
print(new_key.key)

# List all keys (values are masked)
all_keys = snap.keys_list()

# Delete a key
result = snap.keys_delete("key_id")
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

**Exception hierarchy:**

| Exception | HTTP status | When |
|-----------|-------------|------|
| `AuthenticationError` | 401, 403 | Invalid or missing API key |
| `QuotaExceededError` | 402 | Monthly quota exhausted |
| `ValidationError` | 422 | Invalid request parameters (`.fields` for per-field details) |
| `RateLimitError` | 429 | Too many requests (`.retry_after` seconds) |
| `TimeoutError` | — | Request exceeded timeout |
| `NetworkError` | — | DNS failure, connection refused, etc. |
| `SnapAPIError` | any | Base class for all SDK exceptions |

## Advanced Usage

### Proxies

```python
from snapapi import ProxyConfig

# Custom proxy
data = snap.screenshot(
    url="https://example.com",
    proxy=ProxyConfig(server="http://proxy.example.com:8080", username="user", password="pass"),
)

# SnapAPI built-in rotating proxy
data = snap.screenshot(url="https://example.com", premium_proxy=True)
```

### Custom Headers and Cookies

```python
from snapapi import Cookie, HttpAuth

data = snap.screenshot(
    url="https://app.example.com/dashboard",
    extra_headers={"Accept-Language": "fr-FR"},
    cookies=[
        Cookie(
            name="session",
            value="abc123",
            domain="app.example.com",
            secure=True,
            http_only=True,
        )
    ],
    http_auth=HttpAuth(username="admin", password="secret"),
)
```

### Batch Processing

```python
import asyncio
from snapapi import AsyncSnapAPI

async def batch_screenshots(urls: list) -> None:
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

### Async Extract Convenience Methods

```python
import asyncio
from snapapi import AsyncSnapAPI

async def main():
    async with AsyncSnapAPI(api_key="sk_live_...") as snap:
        result = await snap.extract_markdown("https://example.com")
        print(result.content)

        result = await snap.extract_links("https://example.com")
        for link in result.content:
            print(link)

asyncio.run(main())
```

### LLM Data Pipeline

```python
import os

# Extract page content as markdown
content_result = snap.extract(
    url="https://example.com/article",
    type="markdown",
    clean_output=True,
)
print(content_result.content)

# Analyze the page with AI
analysis = snap.analyze(
    url="https://example.com/article",
    prompt="Summarize the key points and sentiment.",
    provider="openai",
    api_key=os.environ["OPENAI_API_KEY"],
)
print(analysis.result)
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
