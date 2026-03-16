# Changelog

All notable changes to the `snapapi` Python SDK are documented here.

## [3.1.0] — 2026-03-16

### Added
- `SnapAPI.screenshot_to_file(url, filepath, **kwargs)` -- capture and save to disk in one call.
- `SnapAPI.pdf_to_file(url, filepath, **kwargs)` -- generate PDF and save to disk in one call.
- `AsyncSnapAPI.screenshot_to_file()` and `AsyncSnapAPI.pdf_to_file()` -- async equivalents.
- `SnapAPI.get_usage()` / `AsyncSnapAPI.get_usage()` -- primary usage method (maps to `/v1/usage`).
- `X-Api-Key` header sent alongside `Authorization: Bearer` for maximum server compatibility.
- Additional unit tests: video, og_image, analyze, screenshot_to_file, pdf_to_file, error class structure, non-retryable error paths.
- Comprehensive README overhaul with full options table, advanced usage patterns, and batch processing examples.

### Changed
- `SnapAPI.quota()` now calls `get_usage()` internally (both remain available).
- HTTP module version bumped to `3.1.0` in User-Agent string.

### Fixed
- Removed duplicate `block_trackers` and `block_chat_widgets` field definitions in `ScreenshotOptions` dataclass.

## [3.0.0] — 2026-03-14

### Breaking Changes
- HTTP transport switched from `urllib` (sync) + `aiohttp` (async) to `httpx` for both.
  **Migration:** replace `pip install aiohttp` with `pip install httpx`.
- `httpx` is now a required dependency (not optional).
- `SnapAPI.get_usage()` deprecated in favour of `SnapAPI.quota()` (correct endpoint).
- `AsyncSnapAPI.scrape()`, `.extract()`, `.analyze()` now accept keyword arguments
  directly (same signature as the sync client), not option dataclasses.
- `VideoOptions.scroll` renamed to `VideoOptions.scrolling`. `scroll` still works as
  a backwards-compat alias.
- Error classes moved from `snapapi.client` to `snapapi.exceptions` (still importable
  from top-level `snapapi`).
- Version bumped to `3.0.0` (major — breaking changes).

### Added
- `snapapi.exceptions` module with full error class hierarchy:
  `SnapAPIError`, `RateLimitError`, `AuthenticationError`, `ValidationError`,
  `QuotaExceededError`, `TimeoutError`, `NetworkError`.
- `SnapAPI.pdf()` — dedicated PDF conversion method.
- `SnapAPI.og_image()` / `AsyncSnapAPI.og_image()` — OG image generation.
- `SnapAPI.quota()` / `AsyncSnapAPI.quota()` — correct `/v1/quota` endpoint.
- `SnapAPI.video()` / `AsyncSnapAPI.video()` — aligned parameter names with JS SDK.
- Automatic retry logic with exponential backoff (configurable `max_retries`,
  `retry_delay`).
- Rate-limit auto-wait: respects `Retry-After` response header on HTTP 429.
- `SnapAPI` context manager: `with SnapAPI(api_key=...) as snap:`.
- `AsyncSnapAPI` context manager: `async with AsyncSnapAPI(api_key=...) as snap:`.
- `SnapAPI.close()` / `AsyncSnapAPI.close()` to release the connection pool.
- `snapapi._http` internal module for shared HTTP helpers.
- `Authorization: Bearer <key>` header (was `X-Api-Key`).
- `httpx` dependency listed in `[project.dependencies]` (was optional `aiohttp`).
- `pytest-asyncio` with `asyncio_mode = "auto"`.
- `respx` for mocking httpx in tests.
- Comprehensive unit test suite (`tests/test_client.py`, `tests/test_async_client.py`).
- Integration test script (`tests/integration.py`).
- `CHANGELOG.md`.

### Changed
- `ScreenshotOptions` and `VideoOptions` extended with v3 fields (`block_trackers`,
  `block_chat_widgets`, `page_size`, `landscape`, `margins`, `scrolling`, `scroll_speed`).
- `ExtractOptions` converted from plain class to `@dataclass`.
- README completely rewritten with tables, async examples, and error-handling section.
- `pyproject.toml` updated with `respx`, `asyncio_mode = "auto"`, and coverage config.

### Fixed
- `AsyncSnapAPI._request()` was not raising for HTTP >= 400 in all paths.
- `RateLimitError.retry_after` was parsed as `str` from headers; now `float`.
- `parse_error_response` now handles both flat and nested API error formats correctly.

## [2.0.0] — 2025-12

- Initial public release with screenshot, scrape, extract, analyze, video, storage,
  scheduled screenshots, webhooks, and API key management.
