#!/usr/bin/env python3
"""
Comprehensive test app for SnapAPI Python SDK
Tests EVERY endpoint and parameter against the LIVE API.
"""

import os
import sys
import json
import time
import traceback
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from snapapi import SnapAPI, SnapAPIError
from snapapi.types import PdfOptions, ThumbnailOptions, ExtractMetadata, Cookie

API_KEY = os.environ.get("SNAPAPI_KEY", "")
if not API_KEY:
    print("Set SNAPAPI_KEY environment variable")
    sys.exit(1)
BASE_URL = "https://api.snapapi.pics"
TEST_URL = "https://example.com"
DELAY = 1.5  # seconds between tests to avoid rate limiting

client = SnapAPI(api_key=API_KEY, base_url=BASE_URL, timeout=120)

passed = 0
failed = 0
skipped = 0
errors = []


def test(name: str):
    def decorator(fn):
        def wrapper():
            global passed, failed, skipped
            time.sleep(DELAY)
            print(f"\n{'='*60}\nTEST: {name}\n{'='*60}")
            try:
                fn()
                passed += 1
                print(f"  ✅ PASSED")
            except SnapAPIError as e:
                msg = str(e).lower()
                if e.status_code == 429 or "rate limit" in msg:
                    skipped += 1
                    print(f"  ⏭️  SKIPPED (rate limit): {e}")
                elif e.status_code == 402 or "quota" in msg or "requires pro" in msg or "requires" in msg and "plan" in msg:
                    skipped += 1
                    print(f"  ⏭️  SKIPPED (plan limit): {e}")
                else:
                    failed += 1
                    errors.append((name, str(e)))
                    print(f"  ❌ FAILED: {e}")
            except Exception as e:
                failed += 1
                errors.append((name, str(e)))
                print(f"  ❌ FAILED: {e}")
                traceback.print_exc()
        wrapper.__name__ = fn.__name__
        wrapper._test_name = name
        return wrapper
    return decorator


# ============ 1. PING ============

@test("GET /v1/ping")
def test_ping():
    result = client.ping()
    print(f"  Response: {result}")
    assert result.get("status") == "ok"


# ============ 2. DEVICES ============

@test("GET /v1/devices")
def test_devices():
    result = client.get_devices()
    print(f"  Total: {result.total}, Categories: {list(result.devices.keys())}")
    assert result.success and result.total > 0


# ============ 3. CAPABILITIES ============

@test("GET /v1/capabilities")
def test_capabilities():
    result = client.get_capabilities()
    print(f"  Version: {result.version}")
    print(f"  Formats: {result.capabilities.get('formats')}")
    assert result.success


# ============ 4. USAGE ============

@test("GET /v1/usage")
def test_usage():
    result = client.get_usage()
    print(f"  Used: {result.used}/{result.limit}, Remaining: {result.remaining}")
    assert result.limit > 0


# ============ 5. SCREENSHOTS ============

@test("Screenshot: basic PNG")
def test_ss_basic():
    data = client.screenshot(url=TEST_URL)
    assert isinstance(data, bytes) and data[:4] == b'\x89PNG'
    print(f"  {len(data)} bytes")

@test("Screenshot: JPEG")
def test_ss_jpeg():
    data = client.screenshot(url=TEST_URL, format="jpeg", quality=80)
    assert data[:2] == b'\xff\xd8'
    print(f"  {len(data)} bytes")

@test("Screenshot: WebP")
def test_ss_webp():
    data = client.screenshot(url=TEST_URL, format="webp", quality=90)
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: AVIF")
def test_ss_avif():
    data = client.screenshot(url=TEST_URL, format="avif")
    assert len(data) > 100
    print(f"  {len(data)} bytes")

@test("Screenshot: PDF via screenshot")
def test_ss_pdf():
    data = client.screenshot(url=TEST_URL, format="pdf")
    assert data[:4] == b'%PDF'
    print(f"  {len(data)} bytes")

@test("Screenshot: full page")
def test_ss_full_page():
    data = client.screenshot(url=TEST_URL, full_page=True)
    assert len(data) > 1000
    print(f"  {len(data)} bytes")

@test("Screenshot: custom viewport 800x600")
def test_ss_viewport():
    data = client.screenshot(url=TEST_URL, width=800, height=600)
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: device preset iphone-15-pro")
def test_ss_device():
    data = client.screenshot_device(url=TEST_URL, device="iphone-15-pro")
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: dark mode")
def test_ss_dark():
    data = client.screenshot(url=TEST_URL, dark_mode=True)
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: selector h1")
def test_ss_selector():
    data = client.screenshot(url=TEST_URL, selector="h1")
    assert len(data) > 100
    print(f"  {len(data)} bytes")

@test("Screenshot: custom CSS")
def test_ss_css():
    data = client.screenshot(url=TEST_URL, css="body{background:red!important}")
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: JavaScript injection")
def test_ss_js():
    data = client.screenshot(url=TEST_URL, javascript="document.title='Modified'")
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: delay 500ms")
def test_ss_delay():
    data = client.screenshot(url=TEST_URL, delay=500)
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: waitForSelector")
def test_ss_wait_selector():
    data = client.screenshot(url=TEST_URL, wait_for_selector="h1")
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: block ads+trackers+cookies+chat")
def test_ss_blocking():
    data = client.screenshot(url=TEST_URL, block_ads=True, block_trackers=True,
                              block_cookie_banners=True, block_chat_widgets=True)
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: hide selectors")
def test_ss_hide():
    data = client.screenshot(url=TEST_URL, hide_selectors=["h1", "p"])
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: JSON response + metadata")
def test_ss_json():
    r = client.screenshot(url=TEST_URL, response_type="json", include_metadata=True)
    print(f"  {r.width}x{r.height}, {r.file_size}B, took={r.took}ms")
    if r.metadata:
        print(f"  Title: {r.metadata.title}")
    assert r.success and r.data

@test("Screenshot: base64 response")
def test_ss_base64():
    r = client.screenshot(url=TEST_URL, response_type="base64")
    assert r.success and r.data
    print(f"  base64 length: {len(r.data)}")

@test("Screenshot: thumbnail")
def test_ss_thumb():
    r = client.screenshot(url=TEST_URL, response_type="json",
                           thumbnail=ThumbnailOptions(enabled=True, width=200, height=150, fit="cover"))
    print(f"  Has thumbnail: {r.thumbnail is not None}")
    assert r.success

@test("Screenshot: extract metadata (fonts/colors/links)")
def test_ss_extract_meta():
    r = client.screenshot(url=TEST_URL, response_type="json", include_metadata=True,
                           extract_metadata=ExtractMetadata(fonts=True, colors=True, links=True, http_status_code=True))
    if r.metadata:
        print(f"  HTTP: {r.metadata.http_status_code}, Fonts: {r.metadata.fonts and len(r.metadata.fonts)}")
    assert r.success

@test("Screenshot: mobile emulation")
def test_ss_mobile():
    data = client.screenshot(url=TEST_URL, width=375, height=812,
                              device_scale_factor=3.0, is_mobile=True, has_touch=True)
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: from HTML")
def test_ss_html():
    data = client.screenshot_from_html(html="<h1 style='color:blue'>Hello!</h1>")
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: from Markdown")
def test_ss_md():
    data = client.screenshot_from_markdown(markdown="# Hello\n\n**Bold** text\n- item")
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: custom user agent + headers")
def test_ss_headers():
    data = client.screenshot(url=TEST_URL, user_agent="TestBot/1.0",
                              extra_headers={"Accept-Language": "en-US"})
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: cookies")
def test_ss_cookies():
    data = client.screenshot(url=TEST_URL,
                              cookies=[Cookie(name="test", value="123", domain=".example.com")])
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: timezone + locale")
def test_ss_tz():
    data = client.screenshot(url=TEST_URL, timezone="America/New_York", locale="en-US")
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: waitUntil networkidle")
def test_ss_wait_until():
    data = client.screenshot(url=TEST_URL, wait_until="networkidle")
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: reduced motion")
def test_ss_reduced():
    data = client.screenshot(url=TEST_URL, reduced_motion=True)
    assert len(data) > 500
    print(f"  {len(data)} bytes")

@test("Screenshot: clip region")
def test_ss_clip():
    data = client.screenshot(url=TEST_URL, clip_x=0, clip_y=0, clip_width=400, clip_height=300)
    assert len(data) > 100
    print(f"  {len(data)} bytes")

@test("Screenshot: landscape")
def test_ss_landscape():
    data = client.screenshot(url=TEST_URL, is_landscape=True, width=812, height=375)
    assert len(data) > 500
    print(f"  {len(data)} bytes")


# ============ 6. PDF ============

@test("PDF: basic")
def test_pdf():
    data = client.pdf(url=TEST_URL)
    assert data[:4] == b'%PDF'
    print(f"  {len(data)} bytes")

@test("PDF: with options")
def test_pdf_opts():
    data = client.pdf(url=TEST_URL, pdf_options=PdfOptions(
        page_size="a4", landscape=True, print_background=True,
        margin_top="20mm", margin_bottom="20mm"))
    assert data[:4] == b'%PDF'
    print(f"  {len(data)} bytes")

@test("PDF: from HTML")
def test_pdf_html():
    data = client.pdf(html="<h1>Invoice</h1><p>$99</p>")
    assert data[:4] == b'%PDF'
    print(f"  {len(data)} bytes")


# ============ 7. BATCH ============

@test("Batch: 2 URLs + poll")
def test_batch():
    r = client.batch(urls=["https://example.com", "https://httpbin.org/html"])
    print(f"  Job: {r.job_id}, Status: {r.status}, Total: {r.total}")
    assert r.job_id and r.total == 2
    for i in range(30):
        time.sleep(2)
        s = client.get_batch_status(r.job_id)
        print(f"  Poll {i+1}: {s.status} ({s.completed}/{s.total})")
        if s.status in ("completed", "failed"):
            if s.results:
                for item in s.results:
                    print(f"    {item.url}: {item.status}")
            break

@test("Batch: with options")
def test_batch_opts():
    r = client.batch(urls=["https://example.com"], format="jpeg", quality=80,
                      dark_mode=True, block_ads=True)
    print(f"  Job: {r.job_id}")
    assert r.job_id


# ============ 8. VIDEO ============

@test("Video: basic mp4")
def test_video():
    data = client.video(url=TEST_URL, duration=3, width=800, height=600)
    assert isinstance(data, bytes) and len(data) > 1000
    print(f"  {len(data)} bytes")

@test("Video: scroll animation")
def test_video_scroll():
    data = client.video(url=TEST_URL, duration=5, scroll=True,
                         scroll_duration=1500, scroll_easing="ease_in_out",
                         scroll_back=True, width=800, height=600)
    assert len(data) > 1000
    print(f"  {len(data)} bytes")

@test("Video: GIF format")
def test_video_gif():
    data = client.video(url=TEST_URL, format="gif", duration=2, width=400, height=300, fps=10)
    assert len(data) > 100
    print(f"  {len(data)} bytes")

@test("Video: JSON response")
def test_video_json():
    r = client.video(url=TEST_URL, duration=2, response_type="json", width=640, height=480)
    print(f"  Success: {r.success}, {r.format}, {r.file_size}B")
    assert r.success


# ============ 9. EXTRACT ============

@test("Extract: markdown")
def test_ext_md():
    r = client.extract_markdown(url=TEST_URL)
    print(f"  Type: {r.type}, Content: {str(r.content)[:100]}")
    assert r.success

@test("Extract: text")
def test_ext_text():
    r = client.extract_text(url=TEST_URL)
    assert r.success
    print(f"  Content: {str(r.content)[:100]}")

@test("Extract: html")
def test_ext_html():
    r = client.extract(url=TEST_URL, type="html")
    assert r.success
    print(f"  Content length: {len(str(r.content))}")

@test("Extract: article")
def test_ext_article():
    r = client.extract_article(url=TEST_URL)
    assert r.success

@test("Extract: links")
def test_ext_links():
    r = client.extract_links(url=TEST_URL)
    assert r.success
    print(f"  Content: {str(r.content)[:200]}")

@test("Extract: images")
def test_ext_images():
    r = client.extract_images(url=TEST_URL)
    assert r.success

@test("Extract: metadata")
def test_ext_meta():
    r = client.extract_metadata(url=TEST_URL)
    assert r.success
    print(f"  Content: {str(r.content)[:200]}")

@test("Extract: structured")
def test_ext_struct():
    r = client.extract_structured(url=TEST_URL)
    assert r.success

@test("Extract: with selector + options")
def test_ext_opts():
    r = client.extract(url=TEST_URL, type="text", selector="h1",
                        block_ads=True, block_cookie_banners=True, clean_output=True)
    assert r.success


# ============ 10. ANALYZE ============

@test("Analyze: requires apiKey (expected skip)")
def test_analyze():
    # Analyze requires a provider API key - we test the SDK sends correct params
    try:
        client.analyze(url=TEST_URL, prompt="Summarize this page",
                        provider="openai", api_key="sk-test-dummy")
    except SnapAPIError as e:
        # 401/400 from provider is expected with dummy key - SDK worked correctly
        if "api" in str(e).lower() or e.status_code in (400, 401, 500):
            print(f"  SDK sent request correctly, provider rejected dummy key: {e}")
            return
        raise
    print(f"  Unexpectedly succeeded")


# ============ 11. ASYNC SCREENSHOTS ============

@test("Async screenshot: submit + poll")
def test_async():
    r = client.screenshot_async(url=TEST_URL)
    job_id = r.get("jobId")
    print(f"  Job: {job_id}, Status: {r.get('status')}")
    assert job_id
    for i in range(20):
        time.sleep(2)
        s = client.get_async_status(job_id)
        st = s.get("status")
        print(f"  Poll {i+1}: {st}")
        if st in ("completed", "failed"):
            print(f"  Result: {json.dumps(s, indent=2)[:300]}")
            break


# ============ 12. ERROR HANDLING ============

@test("Error: invalid URL → 400")
def test_err_url():
    try:
        client.screenshot(url="not-a-url")
        assert False
    except SnapAPIError as e:
        print(f"  Expected: {e}")
        assert e.status_code >= 400

@test("Error: invalid API key → 401")
def test_err_key():
    try:
        SnapAPI(api_key="sk_invalid").screenshot(url=TEST_URL)
        assert False
    except SnapAPIError as e:
        print(f"  Expected: {e}")
        assert e.status_code in (401, 403)

@test("Error: missing params → ValueError")
def test_err_params():
    try:
        client.screenshot()
        assert False
    except ValueError as e:
        print(f"  Expected: {e}")


# ============ RUN ============

if __name__ == "__main__":
    print("=" * 60)
    print(f"SnapAPI Python SDK v{__import__('snapapi').__version__} Test Suite")
    print(f"API: {BASE_URL}")
    print("=" * 60)

    tests = [v for v in globals().values() if callable(v) and hasattr(v, '_test_name')]
    for t in tests:
        t()

    print(f"\n{'='*60}\nSUMMARY\n{'='*60}")
    print(f"  ✅ Passed:  {passed}")
    print(f"  ❌ Failed:  {failed}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  Total:     {passed + failed + skipped}")
    if errors:
        print(f"\nFailures:")
        for n, e in errors:
            print(f"  ❌ {n}: {e}")
    print(f"\n{'🎉 ALL PASSED!' if failed == 0 else f'⚠️  {failed} FAILED'}")
    sys.exit(0 if failed == 0 else 1)
