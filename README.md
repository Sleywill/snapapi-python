# snapapi

Official Python SDK for **[SnapAPI](https://snapapi.pics)** — a lightning-fast screenshot, scrape, extract and AI-analyze API.

## Installation

```bash
pip install snapapi

# With async support (aiohttp)
pip install snapapi[async]
```

## Quick Start

```python
from snapapi import SnapAPI

client = SnapAPI(api_key="sk_live_YOUR_KEY")

# Take a screenshot
buf = client.screenshot(url="https://example.com")
with open("shot.png", "wb") as f:
    f.write(buf)
```

### Async

```python
import asyncio
from snapapi import AsyncSnapAPI

async def main():
    async with AsyncSnapAPI(api_key="sk_live_YOUR_KEY") as client:
        buf = await client.screenshot(url="https://example.com")
        with open("shot.png", "wb") as f:
            f.write(buf)

asyncio.run(main())
```

---

## Authentication

```python
from snapapi import SnapAPI

client = SnapAPI(
    api_key="sk_live_YOUR_KEY",   # required
    base_url="https://api.snapapi.pics",  # optional override
    timeout=60,                    # seconds, default 60
)
```

---

## Methods

### `client.screenshot(...)` → `bytes | dict`

Capture a screenshot of a URL, raw HTML, or Markdown.

| Return type | Trigger |
|---|---|
| `bytes` | Default (binary image/PDF) |
| `dict` with `{id, url}` | `storage=...` is set |
| `dict` with `{jobId, status}` | `webhook_url=...` is set |

```python
# Basic PNG
buf = client.screenshot(url="https://example.com")
open("shot.png", "wb").write(buf)

# Full-page dark-mode WebP
buf = client.screenshot(
    url="https://example.com",
    format="webp",
    full_page=True,
    dark_mode=True,
    block_ads=True,
    block_cookie_banners=True,
    quality=80,
)

# iPhone 15 Pro viewport
buf = client.screenshot(
    url="https://example.com",
    device="iphone-15-pro",
    format="png",
)

# Render raw HTML
buf = client.screenshot(
    html="<h1>Hello!</h1>",
    width=800,
    height=300,
)

# Generate PDF
pdf = client.screenshot(
    url="https://example.com",
    format="pdf",
    page_size="a4",
    margins={"top": "20mm", "bottom": "20mm"},
)
open("page.pdf", "wb").write(pdf)

# Store in SnapAPI cloud
result = client.screenshot(
    url="https://example.com",
    storage={"destination": "snapapi"},
)
print(result["id"], result["url"])

# Async via webhook
queued = client.screenshot(
    url="https://example.com",
    webhook_url="https://my.app/hooks/snapapi",
)
print(queued["jobId"])
```

**Key parameters:**

| Parameter | Type | Description |
|---|---|---|
| `url` | `str` | Page URL |
| `html` | `str` | Raw HTML to render |
| `markdown` | `str` | Markdown to render |
| `format` | `str` | `'png'/'jpeg'/'webp'/'avif'/'pdf'` |
| `quality` | `int` | 1-100 for JPEG/WebP |
| `device` | `str` | 25 device presets |
| `width` / `height` | `int` | Viewport size |
| `full_page` | `bool` | Capture full scrollable page |
| `selector` | `str` | CSS element to capture |
| `delay` | `int` | Wait before capture (ms) |
| `wait_until` | `str` | `'load'/'domcontentloaded'/'networkidle'` |
| `dark_mode` | `bool` | Dark colour scheme |
| `css` / `javascript` | `str` | Inject CSS/JS |
| `hide_selectors` | `list` | Hide elements |
| `block_ads` / `block_trackers` / `block_cookie_banners` | `bool` | Blocking |
| `proxy` | `ProxyConfig` | Custom proxy |
| `premium_proxy` | `bool` | SnapAPI rotating proxy |
| `geolocation` | `Geolocation` | Emulate location |
| `timezone` | `str` | e.g. `'America/New_York'` |
| `http_auth` | `HttpAuth` | HTTP Basic Auth |
| `cookies` | `list[Cookie]` | Inject cookies |
| `extra_headers` | `dict` | Custom request headers |
| `storage` | `dict` | `{"destination": "snapapi"}` |
| `webhook_url` | `str` | Async delivery |
| `page_size` / `landscape` / `margins` | | PDF options |

---

### `client.scrape(options)` → `ScrapeResult`

```python
from snapapi import SnapAPI, ScrapeOptions

client = SnapAPI(api_key="sk_live_YOUR_KEY")

result = client.scrape(ScrapeOptions(
    url="https://news.ycombinator.com",
    type="links",          # 'text' | 'html' | 'links'
    pages=1,
    wait_ms=1000,
    block_resources=True,
))

for page in result.results:
    print(f"Page {page.page}: {page.data[:200]}")
```

---

### `client.extract(options)` → `ExtractResult`

```python
from snapapi import SnapAPI, ExtractOptions

result = client.extract(ExtractOptions(
    url="https://example.com/blog/post",
    type="markdown",       # html|text|markdown|article|links|images|metadata|structured
    clean_output=True,
    max_length=10000,
))

print(result.content)
```

---

### `client.analyze(options)` → `AnalyzeResult` *(BYOK)*

```python
import os
from snapapi import SnapAPI, AnalyzeOptions

result = client.analyze(AnalyzeOptions(
    url="https://example.com",
    prompt="Summarize the main content in 3 bullet points.",
    provider="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    include_screenshot=False,
    include_metadata=True,
))

print(result.result)
```

---

### Storage API

```python
# Take a screenshot and store it
stored = client.screenshot(
    url="https://example.com",
    storage={"destination": "snapapi"},
)
file_id = stored["id"]

# Check usage
usage = client.storage_get_usage()
print(f"{usage.used_formatted} / {usage.limit_formatted} ({usage.percentage}%)")

# List files
listing = client.storage_list_files(limit=10)
for f in listing.files:
    print(f.id, f.url)

# Get a file
file = client.storage_get_file(file_id)
print(file.url)

# Delete a file
result = client.storage_delete_file(file_id)
print(result.success)

# Configure custom S3
from snapapi import S3Config
client.storage_configure_s3(S3Config(
    s3_bucket="my-bucket",
    s3_region="us-east-1",
    s3_access_key_id="AKIA...",
    s3_secret_access_key="secret",
))

# Test S3 connection
test = client.storage_test_s3()
print("S3 OK:", test.success)
```

---

### Scheduled Screenshots

```python
from snapapi import SnapAPI, CreateScheduledOptions

# Create a daily job
job = client.scheduled_create(CreateScheduledOptions(
    url="https://example.com",
    cron_expression="0 9 * * *",    # every day at 09:00 UTC
    format="png",
    full_page=True,
    webhook_url="https://my.app/hooks/snap",
))
print(job.id, job.next_run)

# List jobs
jobs = client.scheduled_list()
for j in jobs:
    print(j.id, j.cron_expression, j.next_run)

# Delete a job
client.scheduled_delete(job.id)
```

---

### Webhooks

```python
from snapapi import CreateWebhookOptions

# Register a webhook
wh = client.webhooks_create(CreateWebhookOptions(
    url="https://my.app/hooks/snapapi",
    events=["screenshot.done"],
    secret="my-signing-secret",
))
print(wh.id)

# List webhooks
webhooks = client.webhooks_list()

# Delete
client.webhooks_delete(wh.id)
```

---

### API Keys

```python
# List (values are masked)
keys = client.keys_list()
for k in keys:
    print(k.name, k.key)

# Create — full key shown only once
new_key = client.keys_create("ci-pipeline")
print("Save this:", new_key.key)

# Delete
client.keys_delete(new_key.id)
```

---

## Error Handling

```python
from snapapi import SnapAPI, SnapAPIError

try:
    buf = client.screenshot(url="https://example.com")
except SnapAPIError as e:
    print(e.code, e.status_code, str(e))
```

---

## Async Client

```python
import asyncio
from snapapi import AsyncSnapAPI, ScrapeOptions, CreateScheduledOptions

async def main():
    async with AsyncSnapAPI(api_key="sk_live_YOUR_KEY") as client:
        # Screenshot
        buf = await client.screenshot(url="https://example.com", dark_mode=True)

        # Scrape
        result = await client.scrape(ScrapeOptions(url="https://example.com", type="text"))

        # Storage
        usage = await client.storage_get_usage()
        print(usage.used_formatted)

        # Scheduled
        job = await client.scheduled_create(CreateScheduledOptions(
            url="https://example.com",
            cron_expression="0 9 * * *",
        ))

asyncio.run(main())
```

---

## Type Reference

```python
from snapapi import (
    ScreenshotOptions, ScrapeOptions, ExtractOptions, AnalyzeOptions,
    StorageFile, StorageUsage, S3Config,
    CreateScheduledOptions, ScheduledScreenshot,
    CreateWebhookOptions, Webhook,
    ApiKey, CreateApiKeyResult,
    Cookie, HttpAuth, ProxyConfig, Geolocation,
)
```

---

## Links

- 🌐 [snapapi.pics](https://snapapi.pics)
- 📖 [API Documentation](https://snapapi.pics/docs)
- 🐛 [Issues](https://github.com/Sleywill/snapapi-python/issues)
- 📦 [JavaScript SDK](https://github.com/Sleywill/snapapi-js)

## License

MIT
