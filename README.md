# snapapi

Official Python SDK for [SnapAPI](https://snapapi.pics) — lightning-fast
screenshot, scrape, extract, PDF, video, and AI-analyze API.

## Installation

```bash
pip install snapapi
```

`httpx` is included as a dependency. No extra installs needed for async support.

## Quick Start

```python
from snapapi import SnapAPI

with SnapAPI(api_key="sk_live_...") as snap:
    buf = snap.screenshot(url="https://example.com")
    with open("shot.png", "wb") as f:
        f.write(buf)
```

## Async

```python
import asyncio
from snapapi import AsyncSnapAPI

async def main():
    async with AsyncSnapAPI(api_key="sk_live_...") as snap:
        buf = await snap.screenshot(url="https://example.com")
        with open("shot.png", "wb") as f:
            f.write(buf)

asyncio.run(main())
```

## Configuration

```python
snap = SnapAPI(
    api_key="sk_live_...",             # required
    base_url="https://snapapi.pics",   # optional override
    timeout=60.0,                       # seconds (default: 60)
    max_retries=3,                      # retries on 429 / 5xx (default: 3)
    retry_delay=0.5,                    # initial backoff seconds (default: 0.5)
)
```

---

## Methods

### `snap.screenshot()`

Capture a screenshot of a URL, HTML string, or Markdown string.

Returns `bytes` for image/PDF responses, or `dict` when `storage` / `webhook_url` is set.

```python
# Basic PNG
buf = snap.screenshot(url="https://example.com")

# Full-page dark-mode WebP
buf = snap.screenshot(
    url="https://example.com",
    format="webp",
    full_page=True,
    dark_mode=True,
    block_ads=True,
    block_cookie_banners=True,
    quality=85,
)

# iPhone 15 Pro viewport
buf = snap.screenshot(url="https://example.com", device="iphone-15-pro")

# Capture a specific element
buf = snap.screenshot(url="https://example.com", selector="#pricing-table")

# From raw HTML
buf = snap.screenshot(html="<h1>Hello!</h1>", width=800, height=200)

# Store in SnapAPI cloud
result = snap.screenshot(
    url="https://example.com",
    storage={"destination": "snapapi"},
)
print(result["url"])  # permanent URL

# Async delivery via webhook
result = snap.screenshot(
    url="https://example.com",
    webhook_url="https://my-app.com/hooks/snap",
)
print(result["jobId"])
```

**Key parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `url` | `str` | — | Page URL |
| `html` | `str` | — | Raw HTML to render |
| `markdown` | `str` | — | Markdown to render |
| `format` | `str` | `'png'` | `'png'`, `'jpeg'`, `'webp'`, `'avif'`, `'pdf'` |
| `quality` | `int` | — | Image quality 1–100 |
| `device` | `str` | — | Device preset (e.g. `'iphone-15-pro'`) |
| `width` / `height` | `int` | 1280 / 800 | Viewport dimensions |
| `full_page` | `bool` | `False` | Capture full scrollable page |
| `selector` | `str` | — | Capture only this CSS element |
| `delay` | `int` | `0` | Wait before capture (ms) |
| `wait_until` | `str` | — | `'load'`, `'domcontentloaded'`, `'networkidle'` |
| `dark_mode` | `bool` | `False` | Dark colour scheme |
| `css` | `str` | — | Inject custom CSS |
| `javascript` | `str` | — | Execute JS before capture |
| `hide_selectors` | `list[str]` | — | Elements to hide |
| `block_ads` | `bool` | `False` | Block ad networks |
| `block_trackers` | `bool` | `False` | Block tracking scripts |
| `block_cookie_banners` | `bool` | `False` | Block consent popups |
| `proxy` | `ProxyConfig` | — | Custom proxy |
| `premium_proxy` | `bool` | `False` | SnapAPI rotating proxy |
| `geolocation` | `Geolocation` | — | GPS coordinates |
| `timezone` | `str` | — | IANA timezone |
| `http_auth` | `HttpAuth` | — | HTTP Basic Auth |
| `cookies` | `list[Cookie]` | — | Inject cookies |
| `extra_headers` | `dict` | — | Custom request headers |
| `storage` | `dict` | — | Store to cloud: `{'destination': 'snapapi'}` |
| `webhook_url` | `str` | — | Async delivery |
| `page_size` | `str` | — | PDF page size (e.g. `'a4'`) |
| `landscape` | `bool` | — | PDF landscape orientation |
| `margins` | `dict` | — | PDF margins: `{'top': '10mm', ...}` |

---

### `snap.pdf()`

Convert a URL or HTML string to a PDF file.

```python
pdf_bytes = snap.pdf(
    url="https://example.com",
    page_size="a4",
    landscape=False,
    margins={"top": "20mm", "bottom": "20mm"},
)
with open("output.pdf", "wb") as f:
    f.write(pdf_bytes)

# From HTML
pdf_bytes = snap.pdf(html="<h1>Invoice</h1>", page_size="letter")
```

---

### `snap.scrape()`

Scrape text, HTML, or links from one or more pages.

```python
result = snap.scrape(
    url="https://news.ycombinator.com",
    type="links",          # 'text' | 'html' | 'links'
    pages=1,
    wait_ms=1000,
    block_resources=True,
)
for page in result.results:
    print(f"Page {page.page}:", page.data[:200])
```

---

### `snap.extract()`

Extract structured content — text, markdown, article, links, images, metadata,
or structured data.

```python
result = snap.extract(
    url="https://example.com/post",
    type="markdown",       # 'text'|'markdown'|'article'|'html'|'links'|'images'|'metadata'|'structured'
    clean_output=True,
    max_length=10_000,
)
print(result.content)
```

---

### `snap.video()`

Record a video of a live webpage.

```python
video_bytes = snap.video(
    url="https://example.com",
    format="mp4",
    duration=5,
    scrolling=True,
    scroll_easing="ease_in_out",
)
with open("recording.mp4", "wb") as f:
    f.write(video_bytes)
```

---

### `snap.og_image()`

Generate an Open Graph image (1200 x 630 by default).

```python
og_bytes = snap.og_image(url="https://example.com")
with open("og.png", "wb") as f:
    f.write(og_bytes)
```

---

### `snap.analyze()`

Analyze a webpage with an LLM (BYOK — bring your own key).

```python
result = snap.analyze(
    url="https://example.com/pricing",
    prompt="List all pricing tiers and their monthly cost.",
    provider="openai",
    api_key="sk-...",
    json_schema={
        "type": "object",
        "properties": {"tiers": {"type": "array"}},
    },
)
print(result.result)
```

---

### `snap.quota()`

Get your API usage for the current billing period.

```python
usage = snap.quota()
print(f"{usage.used} / {usage.limit} calls used ({usage.remaining} remaining)")
```

---

### `snap.storage_*()`

Manage files stored in SnapAPI cloud.

```python
# List files
result = snap.storage_list_files(limit=50, offset=0)

# Get file metadata + download URL
file = snap.storage_get_file("file_id")
print(file.url)

# Delete
snap.storage_delete_file("file_id")

# Usage
usage = snap.storage_get_usage()
print(f"{usage.used_formatted} / {usage.limit_formatted}")

# Configure custom S3
from snapapi import S3Config
snap.storage_configure_s3(S3Config(
    s3_bucket="my-bucket",
    s3_region="us-east-1",
    s3_access_key_id="AKIA...",
    s3_secret_access_key="secret",
))
result = snap.storage_test_s3()
print(result.success)
```

---

### `snap.scheduled_*()`

Manage recurring screenshot jobs.

```python
from snapapi import CreateScheduledOptions

job = snap.scheduled_create(CreateScheduledOptions(
    url="https://example.com",
    cron_expression="0 9 * * *",
    format="png",
    full_page=True,
))
print(job.id, job.next_run)

jobs = snap.scheduled_list()
snap.scheduled_delete(job.id)
```

---

### `snap.webhooks_*()`

Manage webhook endpoints.

```python
from snapapi import CreateWebhookOptions

wh = snap.webhooks_create(CreateWebhookOptions(
    url="https://my-app.com/hooks/snap",
    events=["screenshot.done"],
    secret="signing-secret",
))

webhooks = snap.webhooks_list()
snap.webhooks_delete(wh.id)
```

---

### `snap.keys_*()`

Manage API keys.

```python
keys = snap.keys_list()
result = snap.keys_create("production")
print(result.key)  # full key — store securely!
snap.keys_delete(result.id)
```

---

## Error Handling

All errors extend `SnapAPIError` and include `.code` and `.status_code`:

```python
from snapapi import (
    SnapAPIError,
    RateLimitError,
    AuthenticationError,
    ValidationError,
    QuotaExceededError,
    TimeoutError,
    NetworkError,
)

try:
    buf = snap.screenshot(url="https://example.com")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
    # The SDK retries automatically — you only see this if max_retries is exhausted
except AuthenticationError:
    print("Invalid API key")
except QuotaExceededError:
    print("Quota exhausted — upgrade your plan")
except ValidationError as e:
    print("Bad request:", e.fields)
except TimeoutError:
    print("Request timed out")
except SnapAPIError as e:
    print(f"API error {e.status_code} [{e.code}]: {e.message}")
```

Rate-limit errors (HTTP 429) and server errors (5xx) are **automatically retried**
with exponential backoff. The exception is only raised when all retries are exhausted.

---

## Type Hints

The SDK is fully typed. Import types from the top-level package:

```python
from snapapi import (
    ScreenshotOptions,
    ScrapeOptions,
    ScrapeResult,
    ExtractOptions,
    ExtractResult,
    AnalyzeOptions,
    AnalyzeResult,
    UsageResult,
    Cookie,
    HttpAuth,
    ProxyConfig,
    Geolocation,
    StorageFile,
    ScheduledScreenshot,
    Webhook,
    ApiKey,
)
```

---

## Testing

```bash
pip install "snapapi[dev]"
pytest
```

To run the integration tests against the live API:

```bash
SNAPAPI_KEY=sk_live_... python tests/integration.py
```

---

## License

MIT — see [LICENSE](LICENSE)

## Links

- [snapapi.pics](https://snapapi.pics)
- [API Documentation](https://snapapi.pics/docs)
- [JavaScript SDK](https://github.com/Sleywill/snapapi-js)
- [Issues](https://github.com/Sleywill/snapapi-python/issues)
