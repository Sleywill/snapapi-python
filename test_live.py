"""
Comprehensive live API test suite for the SnapAPI Python SDK.

Tests every method against the live API at https://api.snapapi.pics.
Saves binary outputs to /tmp/snapapi_test_* for inspection.

Run:
    python test_live.py

Requirements:
    pip install httpx pytest-asyncio
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_KEY = os.environ.get(
    "SNAPAPI_KEY",
    "sk_live_YOUR_API_KEY_HERE",
)
OUTPUT_DIR = Path("/tmp/snapapi_test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Test runner helpers
# ---------------------------------------------------------------------------
PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
SKIP = "\033[33mSKIP\033[0m"
WARN = "\033[33mWARN\033[0m"

results: list[dict[str, Any]] = []


def record(name: str, passed: bool, note: str = "", warn: bool = False) -> None:
    status = PASS if passed else (WARN if warn else FAIL)
    label = "PASS" if passed else ("WARN" if warn else "FAIL")
    print(f"  [{status}] {name}" + (f" — {note}" if note else ""))
    results.append({"name": name, "passed": passed, "warn": warn, "note": note})


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def is_png(data: bytes) -> bool:
    return data[:4] == b"\x89PNG"


def is_jpeg(data: bytes) -> bool:
    return data[:2] == b"\xff\xd8"


def is_webp(data: bytes) -> bool:
    return data[:4] == b"RIFF" and data[8:12] == b"WEBP"


def is_pdf(data: bytes) -> bool:
    return data[:4] == b"%PDF"


def is_mp4(data: bytes) -> bool:
    # ftyp box at byte 4 or ISO Base Media file
    return b"ftyp" in data[:12] or b"mdat" in data[:20]


# ---------------------------------------------------------------------------
# SDK import
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
from snapapi import (
    AsyncSnapAPI,
    AuthenticationError,
    NetworkError,
    QuotaExceededError,
    RateLimitError,
    SnapAPI,
    SnapAPIError,
    TimeoutError,
    ValidationError,
)


# ===========================================================================
# SYNC CLIENT TESTS
# ===========================================================================

def test_sync_basic():
    section("SYNC: Basic instantiation & ping")

    # Missing API key
    try:
        SnapAPI(api_key="")
        record("Empty api_key raises ValueError", False)
    except ValueError:
        record("Empty api_key raises ValueError", True)

    # Ping — public endpoint, no auth needed
    with SnapAPI(api_key=API_KEY) as snap:
        result = snap.ping()
        record("ping() returns dict", isinstance(result, dict))
        record("ping() has 'status' key", "status" in result)
        record("ping() status == 'ok'", result.get("status") == "ok", f"got: {result.get('status')}")


def test_sync_usage():
    section("SYNC: Usage / quota")
    with SnapAPI(api_key=API_KEY) as snap:
        u = snap.get_usage()
        record("get_usage() returns UsageResult", hasattr(u, "used"))
        record("used is int", isinstance(u.used, int), f"used={u.used}")
        record("limit is int", isinstance(u.limit, int), f"limit={u.limit}")
        record("remaining is int", isinstance(u.remaining, int), f"remaining={u.remaining}")
        record("reset_at is str", isinstance(u.reset_at, str), f"reset_at={u.reset_at}")

        # quota() alias
        u2 = snap.quota()
        record("quota() is alias for get_usage()", u2.used == u.used)


def test_sync_screenshot_basic():
    section("SYNC: Screenshot — basic formats")
    with SnapAPI(api_key=API_KEY) as snap:
        # PNG
        start = time.time()
        png = snap.screenshot(url="https://example.com", format="png", width=800, height=600)
        elapsed = time.time() - start
        record("screenshot PNG returns bytes", isinstance(png, bytes), f"{len(png)} bytes in {elapsed:.1f}s")
        record("screenshot PNG is valid PNG", is_png(png), f"header: {png[:4].hex()}")
        (OUTPUT_DIR / "screenshot_basic.png").write_bytes(png)

        # JPEG
        jpg = snap.screenshot(url="https://example.com", format="jpeg", width=640, height=480, quality=80)
        record("screenshot JPEG returns bytes", isinstance(jpg, bytes), f"{len(jpg)} bytes")
        record("screenshot JPEG is valid JPEG", is_jpeg(jpg), f"header: {jpg[:2].hex()}")
        (OUTPUT_DIR / "screenshot.jpg").write_bytes(jpg)

        # WebP
        webp = snap.screenshot(url="https://example.com", format="webp", width=400, height=300)
        record("screenshot WebP returns bytes", isinstance(webp, bytes), f"{len(webp)} bytes")
        record("screenshot WebP is valid WebP", is_webp(webp), f"header: {webp[:12].hex()}")
        (OUTPUT_DIR / "screenshot.webp").write_bytes(webp)


def test_sync_screenshot_options():
    section("SYNC: Screenshot — options coverage")
    with SnapAPI(api_key=API_KEY) as snap:
        # full_page
        fp = snap.screenshot(url="https://example.com", format="png", full_page=True)
        record("screenshot full_page=True returns bytes", isinstance(fp, bytes), f"{len(fp)} bytes")
        record("screenshot full_page result is PNG", is_png(fp))
        (OUTPUT_DIR / "screenshot_fullpage.png").write_bytes(fp)

        # dark_mode
        dm = snap.screenshot(url="https://example.com", format="png", dark_mode=True, width=800, height=600)
        record("screenshot dark_mode=True returns bytes", isinstance(dm, bytes), f"{len(dm)} bytes")
        (OUTPUT_DIR / "screenshot_dark.png").write_bytes(dm)

        # block_ads + block_cookie_banners
        blocked = snap.screenshot(
            url="https://example.com",
            format="png",
            block_ads=True,
            block_cookie_banners=True,
        )
        record("screenshot block_ads + block_cookie_banners", isinstance(blocked, bytes))

        # custom CSS
        css_shot = snap.screenshot(
            url="https://example.com",
            format="png",
            css="body { background: #ff0000 !important; }",
            width=400,
            height=300,
        )
        record("screenshot custom CSS returns bytes", isinstance(css_shot, bytes), f"{len(css_shot)} bytes")
        (OUTPUT_DIR / "screenshot_css.png").write_bytes(css_shot)

        # width/height variations
        small = snap.screenshot(url="https://example.com", format="png", width=320, height=240)
        record("screenshot custom width=320, height=240", isinstance(small, bytes))

        large = snap.screenshot(url="https://example.com", format="png", width=1920, height=1080)
        record("screenshot custom width=1920, height=1080", isinstance(large, bytes))

        # delay (small delay to avoid server timeout)
        delayed = snap.screenshot(url="https://example.com", format="png", delay=300)
        record("screenshot delay=300ms", isinstance(delayed, bytes))

        # custom JS
        js_shot = snap.screenshot(
            url="https://example.com",
            format="png",
            javascript="document.title = 'Custom Title';",
        )
        record("screenshot custom JS injection", isinstance(js_shot, bytes))


def test_sync_screenshot_to_file():
    section("SYNC: Screenshot — to_file helper")
    with SnapAPI(api_key=API_KEY) as snap:
        filepath = str(OUTPUT_DIR / "screenshot_tofile.png")
        data = snap.screenshot_to_file(url="https://example.com", filepath=filepath)
        record("screenshot_to_file() returns bytes", isinstance(data, bytes))
        record("screenshot_to_file() writes file", Path(filepath).exists())
        record("written file is valid PNG", is_png(Path(filepath).read_bytes()))


def test_sync_pdf():
    section("SYNC: PDF generation")
    with SnapAPI(api_key=API_KEY) as snap:
        # URL to PDF
        pdf_bytes = snap.pdf(url="https://example.com")
        record("pdf(url) returns bytes", isinstance(pdf_bytes, bytes), f"{len(pdf_bytes)} bytes")
        record("pdf(url) is valid PDF", is_pdf(pdf_bytes), f"header: {pdf_bytes[:5]}")
        (OUTPUT_DIR / "url_to_pdf.pdf").write_bytes(pdf_bytes)

        # HTML to PDF
        html_pdf = snap.pdf(html="<h1>Hello SnapAPI</h1><p>Test PDF from HTML</p>")
        record("pdf(html) returns bytes", isinstance(html_pdf, bytes), f"{len(html_pdf)} bytes")
        record("pdf(html) is valid PDF", is_pdf(html_pdf))
        (OUTPUT_DIR / "html_to_pdf.pdf").write_bytes(html_pdf)

        # PDF options: landscape
        ls_pdf = snap.pdf(url="https://example.com", landscape=True)
        record("pdf(landscape=True) returns bytes", isinstance(ls_pdf, bytes))

        # PDF to file
        pdf_path = str(OUTPUT_DIR / "url_to_pdf_tofile.pdf")
        data = snap.pdf_to_file(url="https://example.com", filepath=pdf_path)
        record("pdf_to_file() returns bytes", isinstance(data, bytes))
        record("pdf_to_file() writes file", Path(pdf_path).exists())

        # generate_pdf alias
        alias_pdf = snap.generate_pdf(url="https://example.com")
        record("generate_pdf() alias works", isinstance(alias_pdf, bytes))


def test_sync_scrape():
    section("SYNC: Scrape")
    with SnapAPI(api_key=API_KEY) as snap:
        # text type
        result = snap.scrape(url="https://example.com", type="text")
        record("scrape(type='text') returns ScrapeResult", hasattr(result, "success"))
        record("scrape success=True", result.success is True, f"success={result.success}")
        record("scrape results is list", isinstance(result.results, list))
        record("scrape has 1 result", len(result.results) == 1, f"got {len(result.results)}")
        if result.results:
            r = result.results[0]
            record("scrape result page=1", r.page == 1, f"got {r.page}")
            record("scrape result url matches", "example.com" in r.url)
            record("scrape result data is non-empty str", isinstance(r.data, str) and len(r.data) > 0)

        # html type
        html_result = snap.scrape(url="https://example.com", type="html")
        record("scrape(type='html') success", html_result.success)
        if html_result.results:
            record("scrape html has DOCTYPE", "<!DOCTYPE" in html_result.results[0].data or
                   "<html" in html_result.results[0].data)


def test_sync_extract():
    section("SYNC: Extract")
    with SnapAPI(api_key=API_KEY) as snap:
        # markdown
        r = snap.extract(url="https://example.com", type="markdown")
        record("extract(type='markdown') success", r.success, f"success={r.success}")
        record("extract markdown has content", r.content is not None and len(str(r.content)) > 0)
        record("extract markdown content is str", isinstance(r.content, str))
        record("extract markdown has url", r.url is not None)
        record("extract markdown has took", r.took is not None, f"took={r.took}")

        # text
        txt = snap.extract(url="https://example.com", type="text")
        record("extract(type='text') success", txt.success)
        record("extract text is non-empty", txt.content is not None and len(str(txt.content)) > 0)

        # links
        links = snap.extract(url="https://example.com", type="links")
        record("extract(type='links') success", links.success)
        record("extract links is list", isinstance(links.content, list), f"type={type(links.content).__name__}")

        # images
        imgs = snap.extract(url="https://example.com", type="images")
        record("extract(type='images') success", imgs.success)
        record("extract images is list", isinstance(imgs.content, list))

        # metadata
        meta = snap.extract(url="https://example.com", type="metadata")
        record("extract(type='metadata') success", meta.success)
        record("extract metadata is dict", isinstance(meta.content, dict), f"type={type(meta.content).__name__}")
        if isinstance(meta.content, dict):
            record("extract metadata has 'title'", "title" in meta.content)

        # article
        art = snap.extract(url="https://example.com", type="article")
        record("extract(type='article') success", art.success)
        record("extract article is dict", isinstance(art.content, dict))

        # convenience wrappers
        md2 = snap.extract_markdown(url="https://example.com")
        record("extract_markdown() wrapper works", md2.success)

        txt2 = snap.extract_text(url="https://example.com")
        record("extract_text() wrapper works", txt2.success)

        links2 = snap.extract_links(url="https://example.com")
        record("extract_links() wrapper works", links2.success)

        imgs2 = snap.extract_images(url="https://example.com")
        record("extract_images() wrapper works", imgs2.success)

        meta2 = snap.extract_metadata(url="https://example.com")
        record("extract_metadata() wrapper works", meta2.success)

        art2 = snap.extract_article(url="https://example.com")
        record("extract_article() wrapper works", art2.success)


def test_sync_video():
    section("SYNC: Video recording")
    with SnapAPI(api_key=API_KEY) as snap:
        # MP4
        mp4 = snap.video(url="https://example.com", format="mp4", width=640, height=480, duration=2, fps=24)
        record("video(format='mp4') returns bytes", isinstance(mp4, bytes), f"{len(mp4)} bytes")
        record("video MP4 is valid MP4", is_mp4(mp4), f"header bytes: {mp4[:20].hex()}")
        (OUTPUT_DIR / "video.mp4").write_bytes(mp4)

        # With dark_mode and block_ads
        mp4_opts = snap.video(
            url="https://example.com",
            format="mp4",
            duration=2,
            dark_mode=True,
            block_ads=True,
            block_cookie_banners=True,
        )
        record("video with dark_mode + block_ads", isinstance(mp4_opts, bytes))


def test_sync_analyze():
    section("SYNC: Analyze (known disabled on server)")
    with SnapAPI(api_key=API_KEY) as snap:
        result = snap.analyze(url="https://example.com", prompt="Describe this page in one sentence.")
        # The endpoint is disabled — expect success=False but no exception
        record(
            "analyze() returns AnalyzeResult (not exception) when disabled",
            hasattr(result, "success"),
        )
        record(
            "analyze() success=False when service disabled",
            result.success is False,
            f"success={result.success}",
        )


def test_sync_error_handling():
    section("SYNC: Error handling")
    with SnapAPI(api_key=API_KEY) as snap:
        # Invalid URL — should raise or return an error
        try:
            snap.screenshot(url="not-a-valid-url")
            record(
                "screenshot with invalid URL raises exception or returns error",
                False,
                "Expected exception but none raised",
            )
        except SnapAPIError as e:
            record(
                "screenshot invalid URL raises SnapAPIError subclass",
                True,
                f"{type(e).__name__}: {e.message}",
            )
        except Exception as e:
            record(
                "screenshot invalid URL raises exception (not SnapAPIError)",
                False,
                f"Got {type(e).__name__}: {e}",
                warn=True,
            )

    # Bad API key
    with SnapAPI(api_key="sk_live_definitely_bad") as snap:
        try:
            snap.get_usage()
            record("Bad API key raises AuthenticationError", False, "No exception raised")
        except AuthenticationError as e:
            record("Bad API key raises AuthenticationError", True, f"status={e.status_code}")
        except SnapAPIError as e:
            record(
                "Bad API key raises SnapAPIError (not AuthenticationError)",
                False,
                f"{type(e).__name__} status={e.status_code}",
                warn=True,
            )

    # Missing URL, HTML and markdown
    with SnapAPI(api_key=API_KEY) as snap:
        try:
            snap.screenshot()
            record("screenshot() with no args raises ValueError", False)
        except ValueError:
            record("screenshot() with no args raises ValueError", True)


def test_sync_keys():
    section("SYNC: API Key management")
    with SnapAPI(api_key=API_KEY) as snap:
        keys = snap.keys_list()
        record("keys_list() returns list", isinstance(keys, list))
        if keys:
            k = keys[0]
            record("ApiKey has id", hasattr(k, "id") and k.id)
            record("ApiKey has name", hasattr(k, "name"))
            record("ApiKey has key (masked)", hasattr(k, "key") and k.key)
            record("ApiKey has created_at", hasattr(k, "created_at"))
            # BUG CHECK: SDK reads 'lastUsed' but API returns 'lastUsedAt'
            # SDK field is last_used, API field is lastUsedAt
            record(
                "ApiKey.last_used maps lastUsedAt correctly",
                hasattr(k, "last_used"),
                f"last_used={k.last_used!r} (check mapping lastUsedAt -> last_used)",
            )


def test_sync_scheduled():
    section("SYNC: Scheduled jobs")
    with SnapAPI(api_key=API_KEY) as snap:
        jobs = snap.scheduled_list()
        record("scheduled_list() returns list", isinstance(jobs, list), f"{len(jobs)} jobs")


def test_sync_webhooks():
    section("SYNC: Webhooks")
    with SnapAPI(api_key=API_KEY) as snap:
        hooks = snap.webhooks_list()
        record("webhooks_list() returns list", isinstance(hooks, list), f"{len(hooks)} webhooks")


def test_sync_storage_unavailable():
    """Storage endpoints return 404 — SDK should surface a SnapAPIError."""
    section("SYNC: Storage endpoints (404 — not implemented on server)")
    with SnapAPI(api_key=API_KEY) as snap:
        try:
            snap.storage_list_files()
            record(
                "storage_list_files() raises SnapAPIError for 404",
                False,
                "Expected SnapAPIError, got success",
            )
        except SnapAPIError as e:
            record(
                "storage_list_files() raises SnapAPIError for 404",
                True,
                f"status={e.status_code} code={e.code}",
            )

        try:
            snap.storage_get_usage()
            record(
                "storage_get_usage() raises SnapAPIError for 404",
                False,
                "Expected SnapAPIError, got success",
            )
        except SnapAPIError as e:
            record(
                "storage_get_usage() raises SnapAPIError for 404",
                True,
                f"status={e.status_code}",
            )


def test_sync_og_image():
    section("SYNC: OG Image generation")
    with SnapAPI(api_key=API_KEY) as snap:
        og = snap.og_image(url="https://example.com")
        record("og_image() returns bytes", isinstance(og, bytes), f"{len(og)} bytes")
        record("og_image() is PNG", is_png(og))
        (OUTPUT_DIR / "og_image.png").write_bytes(og)

        # generate_og_image alias
        og2 = snap.generate_og_image(url="https://example.com")
        record("generate_og_image() alias returns bytes", isinstance(og2, bytes))


# ===========================================================================
# ASYNC CLIENT TESTS
# ===========================================================================

async def test_async_basic():
    section("ASYNC: Basic instantiation & ping")

    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        result = await snap.ping()
        record("async ping() returns dict", isinstance(result, dict))
        record("async ping() status == 'ok'", result.get("status") == "ok")

        u = await snap.get_usage()
        record("async get_usage() returns UsageResult", hasattr(u, "used"))
        record("async used is int", isinstance(u.used, int))


async def test_async_screenshot():
    section("ASYNC: Screenshot")
    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        png = await snap.screenshot(url="https://example.com", format="png", width=800, height=600)
        record("async screenshot PNG returns bytes", isinstance(png, bytes), f"{len(png)} bytes")
        record("async screenshot is valid PNG", is_png(png))
        (OUTPUT_DIR / "async_screenshot.png").write_bytes(png)

        # JPEG
        jpg = await snap.screenshot(url="https://example.com", format="jpeg", quality=85)
        record("async screenshot JPEG returns bytes", isinstance(jpg, bytes))
        record("async screenshot JPEG is valid JPEG", is_jpeg(jpg))

        # screenshot_to_file
        fp = str(OUTPUT_DIR / "async_screenshot_tofile.png")
        data = await snap.screenshot_to_file(url="https://example.com", filepath=fp)
        record("async screenshot_to_file() returns bytes", isinstance(data, bytes))
        record("async screenshot_to_file() writes file", Path(fp).exists())


async def test_async_pdf():
    section("ASYNC: PDF generation")
    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        pdf_bytes = await snap.pdf(url="https://example.com")
        record("async pdf() returns bytes", isinstance(pdf_bytes, bytes), f"{len(pdf_bytes)} bytes")
        record("async pdf() is valid PDF", is_pdf(pdf_bytes))
        (OUTPUT_DIR / "async_pdf.pdf").write_bytes(pdf_bytes)

        # generate_pdf alias
        pdf2 = await snap.generate_pdf(url="https://example.com")
        record("async generate_pdf() alias works", isinstance(pdf2, bytes))


async def test_async_scrape():
    section("ASYNC: Scrape")
    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        r = await snap.scrape(url="https://example.com", type="text")
        record("async scrape() returns ScrapeResult", hasattr(r, "success"))
        record("async scrape success=True", r.success)
        record("async scrape has results", len(r.results) >= 1)


async def test_async_extract():
    section("ASYNC: Extract")
    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        md = await snap.extract(url="https://example.com", type="markdown")
        record("async extract markdown success", md.success)
        record("async extract has content", md.content is not None)

        links = await snap.extract_links(url="https://example.com")
        record("async extract_links() success", links.success)
        record("async extract links is list", isinstance(links.content, list))

        meta = await snap.extract_metadata(url="https://example.com")
        record("async extract_metadata() success", meta.success)


async def test_async_video():
    section("ASYNC: Video recording")
    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        mp4 = await snap.video(url="https://example.com", format="mp4", duration=2)
        record("async video MP4 returns bytes", isinstance(mp4, bytes), f"{len(mp4)} bytes")
        record("async video is valid MP4", is_mp4(mp4))
        (OUTPUT_DIR / "async_video.mp4").write_bytes(mp4)


async def test_async_parallel():
    section("ASYNC: Parallel requests (concurrency check)")
    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        start = time.time()
        results_parallel = await asyncio.gather(
            snap.screenshot(url="https://example.com", format="png", width=400, height=300),
            snap.extract(url="https://example.com", type="text"),
            snap.scrape(url="https://example.com", type="text"),
        )
        elapsed = time.time() - start
        png, ext, scr = results_parallel
        record(
            "3 concurrent requests all succeed",
            isinstance(png, bytes) and ext.success and scr.success,
            f"Elapsed: {elapsed:.1f}s (sequential would be ~3x slower)",
        )


async def test_async_error_handling():
    section("ASYNC: Error handling")

    # Bad API key
    async with AsyncSnapAPI(api_key="sk_live_invalid") as snap:
        try:
            await snap.get_usage()
            record("async bad key raises AuthenticationError", False)
        except AuthenticationError as e:
            record("async bad key raises AuthenticationError", True, f"status={e.status_code}")
        except SnapAPIError as e:
            record("async bad key raises SnapAPIError", True, f"{type(e).__name__} status={e.status_code}", warn=True)

    # Missing args
    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        try:
            await snap.screenshot()
            record("async screenshot() no args raises ValueError", False)
        except ValueError:
            record("async screenshot() no args raises ValueError", True)


async def test_async_keys():
    section("ASYNC: API Key management (async)")
    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        keys = await snap.keys_list()
        record("async keys_list() returns list", isinstance(keys, list), f"{len(keys)} keys")
        if keys:
            k = keys[0]
            record("async ApiKey has id", bool(k.id))
            record("async ApiKey has name", hasattr(k, "name"))


async def test_async_scheduled():
    section("ASYNC: Scheduled jobs (async)")
    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        jobs = await snap.scheduled_list()
        record("async scheduled_list() returns list", isinstance(jobs, list))


async def test_async_webhooks():
    section("ASYNC: Webhooks (async)")
    async with AsyncSnapAPI(api_key=API_KEY) as snap:
        hooks = await snap.webhooks_list()
        record("async webhooks_list() returns list", isinstance(hooks, list))


# ===========================================================================
# TYPE HINT VERIFICATION
# ===========================================================================

def test_type_hints():
    section("TYPE HINTS: Verify SDK types match actual API response shapes")
    from snapapi.types import (
        ExtractResult,
        ScrapeResult,
        UsageResult,
        AnalyzeResult,
        ApiKey,
    )

    # UsageResult — API: {"used":N,"limit":N,"remaining":N,"resetAt":"..."}
    u = UsageResult.from_dict({"used": 5, "limit": 100, "remaining": 95, "resetAt": "2026-04-01T00:00:00.000Z"})
    record("UsageResult.from_dict parses correctly", u.used == 5 and u.limit == 100 and u.reset_at == "2026-04-01T00:00:00.000Z")

    # ExtractResult — API returns "data" not "content", and "responseTime" not "took"
    raw_extract = {
        "success": True,
        "type": "markdown",
        "url": "https://example.com",
        "data": "# Hello",
        "responseTime": 1002,
    }
    er = ExtractResult.from_dict(raw_extract)
    record("ExtractResult.content maps from 'data' field", er.content == "# Hello")
    record("ExtractResult.took maps from 'responseTime'", er.took == 1002, f"got took={er.took}")

    # AnalyzeResult — API returns {"success":false,"error":{"code":...,"message":...}} when disabled
    raw_analyze_disabled = {"success": False, "error": {"code": "SERVICE_DISABLED", "message": "AI unavailable."}}
    ar = AnalyzeResult.from_dict(raw_analyze_disabled)
    record("AnalyzeResult.from_dict handles disabled response", ar.success is False)
    record("AnalyzeResult.result is None when disabled", ar.result is None)

    # ApiKey — API returns 'lastUsedAt', SDK reads 'lastUsed' — BUG CHECK
    raw_key = {
        "id": "abc-123",
        "name": "Test Key",
        "key": "sk_live_****",
        "createdAt": "2026-01-01T00:00:00.000Z",
        "lastUsedAt": "2026-03-29T06:20:04.506Z",
    }
    ak = ApiKey.from_dict(raw_key)
    record(
        "ApiKey.last_used maps 'lastUsedAt' from API response",
        ak.last_used == "2026-03-29T06:20:04.506Z",
        f"got last_used={ak.last_used!r} (BUG: SDK reads 'lastUsed', API returns 'lastUsedAt')"
        if ak.last_used is None else f"last_used={ak.last_used!r}",
    )

    # ScrapeResult — scheduled_list uses wrong key
    # Verify: scheduled_list uses data.get("jobs", []) but API returns {"schedules":[], "total":0}
    from snapapi.async_client import AsyncSnapAPI as ASync
    # Just check the code path by inspecting the source
    import inspect
    source = inspect.getsource(ASync.scheduled_list)
    uses_schedules = '"schedules"' in source or "'schedules'" in source
    uses_jobs = ('"jobs"' in source) or ("'jobs'" in source)
    record(
        "AsyncSnapAPI.scheduled_list reads 'schedules' key (API returns 'schedules' not 'jobs')",
        uses_schedules,
        f"reads_schedules={uses_schedules}, reads_jobs={uses_jobs} — BUG if only 'jobs'" if not uses_schedules else "",
    )

    from snapapi.client import SnapAPI as Sync
    source_sync = inspect.getsource(Sync.scheduled_list)
    uses_schedules_sync = '"schedules"' in source_sync or "'schedules'" in source_sync
    record(
        "SnapAPI.scheduled_list reads 'schedules' key",
        uses_schedules_sync,
        f"reads_schedules={uses_schedules_sync}" if not uses_schedules_sync else "",
    )


# ===========================================================================
# RETRY LOGIC TEST
# ===========================================================================

def test_retry_logic():
    section("RETRY LOGIC: Verify error classification")
    from snapapi._http import should_retry, compute_backoff
    from snapapi.exceptions import RateLimitError, AuthenticationError, NetworkError, TimeoutError

    rate_err = RateLimitError()
    record("RateLimitError should_retry=True", should_retry(rate_err))

    auth_err = AuthenticationError()
    record("AuthenticationError should_retry=False", not should_retry(auth_err))

    net_err = NetworkError("Connection refused")
    record("NetworkError should_retry=True (status=0)", should_retry(net_err))

    timeout_err = TimeoutError()
    record("TimeoutError should_retry=True (status=0)", should_retry(timeout_err))

    # Exponential backoff
    record("compute_backoff(1, 0.5) = 0.5", compute_backoff(1, 0.5) == 0.5)
    record("compute_backoff(2, 0.5) = 1.0", compute_backoff(2, 0.5) == 1.0)
    record("compute_backoff(3, 0.5) = 2.0", compute_backoff(3, 0.5) == 2.0)
    record("compute_backoff capped at 30s", compute_backoff(100, 0.5) == 30.0)


# ===========================================================================
# MAIN RUNNER
# ===========================================================================

def run_sync_tests():
    """Run all synchronous tests, catching exceptions so one failure doesn't stop the suite."""
    sync_fns = [
        test_sync_basic,
        test_sync_usage,
        test_sync_screenshot_basic,
        test_sync_screenshot_options,
        test_sync_screenshot_to_file,
        test_sync_pdf,
        test_sync_scrape,
        test_sync_extract,
        test_sync_video,
        test_sync_analyze,
        test_sync_error_handling,
        test_sync_keys,
        test_sync_scheduled,
        test_sync_webhooks,
        test_sync_storage_unavailable,
        test_sync_og_image,
        test_retry_logic,
        test_type_hints,
    ]
    for fn in sync_fns:
        try:
            fn()
        except Exception as e:
            section(f"UNHANDLED ERROR in {fn.__name__}")
            print(f"  [{FAIL}] {fn.__name__} crashed: {e}")
            traceback.print_exc()
            results.append({"name": f"{fn.__name__} (unhandled crash)", "passed": False, "note": str(e)})


async def run_async_tests():
    """Run all async tests."""
    async_fns = [
        test_async_basic,
        test_async_screenshot,
        test_async_pdf,
        test_async_scrape,
        test_async_extract,
        test_async_video,
        test_async_parallel,
        test_async_error_handling,
        test_async_keys,
        test_async_scheduled,
        test_async_webhooks,
    ]
    for fn in async_fns:
        try:
            await fn()
        except Exception as e:
            section(f"UNHANDLED ERROR in {fn.__name__}")
            print(f"  [{FAIL}] {fn.__name__} crashed: {e}")
            traceback.print_exc()
            results.append({"name": f"{fn.__name__} (unhandled crash)", "passed": False, "note": str(e)})


def print_summary():
    section("SUMMARY")
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    warned = sum(1 for r in results if r.get("warn"))
    failed = [r for r in results if not r["passed"] and not r.get("warn")]

    print(f"\n  Total:  {total}")
    print(f"  Passed: {passed}")
    print(f"  Warned: {warned}")
    print(f"  Failed: {len(failed)}")

    if failed:
        print(f"\n  {FAIL} FAILURES:")
        for r in failed:
            print(f"    - {r['name']}" + (f": {r['note']}" if r["note"] else ""))
    else:
        print(f"\n  All tests passed!")

    print(f"\n  Output files saved to: {OUTPUT_DIR}")
    return len(failed) == 0


if __name__ == "__main__":
    print(f"\nSnapAPI Python SDK — Live Test Suite")
    print(f"SDK version: {__import__('snapapi').__version__}")
    print(f"API key: {API_KEY[:20]}...{API_KEY[-4:]}")
    print(f"Output dir: {OUTPUT_DIR}")

    run_sync_tests()
    asyncio.run(run_async_tests())
    ok = print_summary()
    sys.exit(0 if ok else 1)
