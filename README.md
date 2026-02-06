# snapapi

Official Python SDK for [SnapAPI](https://snapapi.pics) - Lightning-fast screenshot API for developers.

## Installation

```bash
pip install snapapi
```

## Quick Start

```python
from snapapi import SnapAPI

client = SnapAPI(api_key='sk_live_xxx')

# Capture a screenshot
screenshot = client.screenshot(url='https://example.com')

# Save to file
with open('screenshot.png', 'wb') as f:
    f.write(screenshot)
```

## Usage Examples

### Basic Screenshot

```python
screenshot = client.screenshot(url='https://example.com')
```

### Full Page Screenshot

```python
screenshot = client.screenshot(
    url='https://example.com',
    full_page=True,
    format='png'
)
```

### Mobile Screenshot

```python
screenshot = client.screenshot(
    url='https://example.com',
    width=375,
    height=812,
    mobile=True,
    scale=3  # Retina
)
```

### Dark Mode

```python
screenshot = client.screenshot(
    url='https://example.com',
    dark_mode=True
)
```

### PDF Export

```python
pdf = client.screenshot(
    url='https://example.com',
    format='pdf',
    full_page=True
)

with open('document.pdf', 'wb') as f:
    f.write(pdf)
```

### Block Ads & Cookies

```python
screenshot = client.screenshot(
    url='https://example.com',
    block_ads=True,
    hide_cookie_banners=True
)
```

### Custom JavaScript Execution

```python
screenshot = client.screenshot(
    url='https://example.com',
    javascript='''
        document.querySelector('.popup')?.remove();
        document.body.style.background = 'white';
    ''',
    delay=1000
)
```

### With Cookies (Authenticated Pages)

```python
from snapapi import Cookie

screenshot = client.screenshot(
    url='https://example.com/dashboard',
    cookies=[
        Cookie(
            name='session',
            value='abc123',
            domain='example.com'
        )
    ]
)
```

### Get JSON Response with Metadata

```python
result = client.screenshot(
    url='https://example.com',
    response_type='json'
)

print(result.width)      # 1920
print(result.height)     # 1080
print(result.file_size)  # 45321
print(result.duration)   # 523
print(result.data)       # base64 encoded image
```

### Batch Screenshots

```python
batch = client.batch(
    urls=[
        'https://example.com',
        'https://example.org',
        'https://example.net'
    ],
    format='png',
    webhook_url='https://your-server.com/webhook'
)

print(batch.job_id)  # 'job_abc123'

# Check status later
status = client.get_batch_status(batch.job_id)
if status.status == 'completed':
    print(status.results)
```

### Screenshot from Markdown

```python
# Render Markdown content as a screenshot
screenshot = client.screenshot_from_markdown(
    markdown='# Hello World\n\nThis is **bold** text.',
    width=800,
    height=600
)

with open('markdown.png', 'wb') as f:
    f.write(screenshot)

# Or use the screenshot method directly
screenshot = client.screenshot(
    markdown='## My Document\n\n- Item 1\n- Item 2',
    format='png'
)
```

### Extract Content

Extract structured content from any web page.

```python
# Extract as Markdown
result = client.extract_markdown(url='https://example.com')
print(result.content)

# Extract article content
result = client.extract_article(url='https://blog.example.com/post')
print(result.content)

# Extract plain text
result = client.extract_text(url='https://example.com')
print(result.content)

# Extract structured data
result = client.extract_structured(url='https://example.com')
print(result.content)

# Extract all links
result = client.extract_links(url='https://example.com')
print(result.content)

# Extract all images
result = client.extract_images(url='https://example.com')
print(result.content)

# Extract page metadata
result = client.extract_metadata(url='https://example.com')
print(result.content)

# Full control with the extract method
result = client.extract(
    url='https://example.com',
    type='markdown',
    selector='article',
    block_ads=True,
    block_cookie_banners=True,
    clean_output=True
)
```

### Analyze with AI

Use AI to analyze web page content.

```python
# Analyze a page with a prompt
result = client.analyze(
    url='https://example.com',
    prompt='Summarize the main content of this page',
    provider='openai',
    api_key='sk-...'
)
print(result.result)

# Get structured JSON output
result = client.analyze(
    url='https://example.com/products',
    prompt='Extract all product names and prices',
    provider='openai',
    api_key='sk-...',
    json_schema={
        'type': 'object',
        'properties': {
            'products': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'price': {'type': 'number'}
                    }
                }
            }
        }
    }
)
print(result.result)

# Include screenshot and metadata
result = client.analyze(
    url='https://example.com',
    prompt='Describe the visual layout of this page',
    provider='anthropic',
    api_key='sk-ant-...',
    include_screenshot=True,
    include_metadata=True
)
print(result.result)
print(result.screenshot)  # base64 encoded screenshot
print(result.metadata)    # page metadata dict
```

## Configuration Options

### Client Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | str | *required* | Your API key |
| `base_url` | str | `https://api.snapapi.pics` | API base URL |
| `timeout` | int | `60` | Request timeout in seconds |

### Screenshot Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `url` | str | *required* | URL to capture |
| `format` | str | `'png'` | `'png'`, `'jpeg'`, `'webp'`, `'avif'`, `'pdf'` |
| `width` | int | `1920` | Viewport width (100-3840) |
| `height` | int | `1080` | Viewport height (100-2160) |
| `full_page` | bool | `False` | Capture full scrollable page |
| `quality` | int | `80` | Image quality 1-100 (JPEG/WebP) |
| `scale` | float | `1.0` | Device scale factor 0.5-3 |
| `delay` | int | `0` | Delay before capture (0-10000ms) |
| `timeout` | int | `30000` | Max wait time (1000-60000ms) |
| `dark_mode` | bool | `False` | Emulate dark mode |
| `mobile` | bool | `False` | Emulate mobile device |
| `selector` | str | `None` | CSS selector for element capture |
| `wait_for_selector` | str | `None` | Wait for element before capture |
| `javascript` | str | `None` | JS to execute before capture |
| `block_ads` | bool | `False` | Block ads and trackers |
| `hide_cookie_banners` | bool | `False` | Hide cookie banners |
| `cookies` | list | `None` | Cookies to set |
| `headers` | dict | `None` | Custom HTTP headers |
| `response_type` | str | `'binary'` | `'binary'`, `'base64'`, `'json'` |

## Error Handling

```python
from snapapi import SnapAPI, SnapAPIError

try:
    client.screenshot(url='invalid-url')
except SnapAPIError as e:
    print(e.code)        # 'INVALID_URL'
    print(e.status_code) # 400
    print(e.message)     # 'The provided URL is not valid'
    print(e.details)     # {'url': 'invalid-url'}
```

### Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_URL` | 400 | URL is malformed or not accessible |
| `INVALID_PARAMS` | 400 | One or more parameters are invalid |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | API key doesn't have permission |
| `QUOTA_EXCEEDED` | 429 | Monthly quota exceeded |
| `RATE_LIMITED` | 429 | Too many requests |
| `TIMEOUT` | 504 | Page took too long to load |
| `CAPTURE_FAILED` | 500 | Screenshot capture failed |

## Type Hints

The SDK includes full type hints for better IDE support:

```python
from snapapi import SnapAPI, ScreenshotOptions, ScreenshotResult

client: SnapAPI = SnapAPI(api_key='sk_live_xxx')

result: ScreenshotResult = client.screenshot(
    url='https://example.com',
    response_type='json'
)
```

## License

MIT
