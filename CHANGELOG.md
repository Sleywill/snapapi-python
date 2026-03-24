# Changelog

All notable changes to the `snapapi` Python SDK are documented here.

## [3.2.0] — 2026-03-23

### Added
- `SnapAPI.generate_pdf()` / `AsyncSnapAPI.generate_pdf()` -- alias for `pdf()` matching the documented SDK interface.
- `SnapAPI.generate_og_image()` / `AsyncSnapAPI.generate_og_image()` -- alias for `og_image()` matching the documented SDK interface.
- `py.typed` marker file (PEP 561) for downstream type checking support.
- Retry logic unit tests: verifies retry on 429, 500, and network errors; verifies no retry on 401 and 422; verifies retry exhaustion behavior.
- Async alias tests for `generate_pdf()` and `generate_og_image()`.
- Test count increased from 115 to 122.

### Changed
- Version bumped to 3.2.0.
- User-Agent string updated to `snapapi-python/3.2.0`.

## [3.1.0] — 2026-03-17

### Added
- `SnapAPI.screenshot_to_storage(url, destination, **kwargs)` and `AsyncSnapAPI.screenshot_to_storage()` -- capture a screenshot and store it in SnapAPI cloud or your S3 bucket. Returns a dict with the public URL.
- `SnapAPI.screenshot_to_file(url, filepath, **kwargs)` and `AsyncSnapAPI.screenshot_to_file()` -- capture and save to disk in one call.
- `SnapAPI.pdf_to_file(url, filepath, **kwargs)` and `AsyncSnapAPI.pdf_to_file()` -- generate PDF and save to disk in one call.
- Extract convenience methods on both clients: `extract_markdown`, `extract_article`, `extract_text`, `extract_links`, `extract_images`, `extract_metadata`. Each is a typed wrapper around `extract(type=...)`.
- `SnapAPI.get_usage()` / `AsyncSnapAPI.get_usage()` -- primary usage method (maps to `/v1/usage`).
- `X-Api-Key` header sent alongside `Authorization: Bearer` for maximum server compatibility.
- Comprehensive unit tests for all storage, scheduled, webhooks, and keys endpoints in both sync and async clients.
- Network error and timeout error test coverage for both clients.
- Test coverage now meets the 80% threshold (80.25%).

### Changed
- Default `base_url` corrected from `https://snapapi.pics` to `https://api.snapapi.pics`.
- `SnapAPI.quota()` now calls `get_usage()` internally (both remain available).
- `ScreenshotOptions.timeout` field type changed from `int` to `Optional[int]` (default `None`) so that the server's default timeout applies when not specified, rather than always sending `30000`.
- HTTP module version bumped to `3.1.0` in User-Agent string.
- README fully corrected: all code examples now match the actual implementation (storage methods, extract return field `.content` not `.data`, analyze return field `.result` not `.analysis`, storage/scheduled/webhooks/keys use flat method names not sub-namespace objects, PDF margins use `margins` dict not individual keyword args, `screenshot_to_storage` returns a dict not a dataclass).

### Fixed
- README example `result.data` for extract corrected to `result.content`.
- README example `result.analysis` for analyze corrected to `result.result`.
- README sub-namespace style calls (`snap.storage.list_files()`) corrected to flat method calls (`snap.storage_list_files()`).
- README PDF example `margin_top` / `margin_bottom` kwargs do not exist on `pdf()` -- corrected to use `margins={"top": ..., "bottom": ...}`.
- README `screenshot_to_storage()` return value corrected from `result.url` to `result["url"]` (returns `dict`, not dataclass).
- `ScreenshotOptions.to_dict()` was unconditionally skipping `timeout` when it was `None`; now only emits `timeout` when set.
- Removed duplicate `block_trackers` and `block_chat_widgets` field serialization in `ScreenshotOptions.to_dict()`.
- Pytest warning about `pytestmark = pytest.mark.asyncio` applied to non-async test -- removed module-level mark (superseded by `asyncio_mode = "auto"` in `pyproject.toml`).

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
