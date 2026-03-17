"""
Type definitions for SnapAPI Python SDK
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

# Device preset type
DevicePreset = Literal[
    "desktop-1080p", "desktop-1440p", "desktop-4k",
    "macbook-pro-13", "macbook-pro-16", "imac-24",
    "iphone-se", "iphone-12", "iphone-13", "iphone-14", "iphone-14-pro",
    "iphone-15", "iphone-15-pro", "iphone-15-pro-max",
    "ipad", "ipad-mini", "ipad-air", "ipad-pro-11", "ipad-pro-12.9",
    "pixel-7", "pixel-8", "pixel-8-pro",
    "samsung-galaxy-s23", "samsung-galaxy-s24", "samsung-galaxy-tab-s9",
]


@dataclass
class Cookie:
    """Cookie configuration for authenticated screenshots."""
    name: str
    value: str
    domain: str | None = None
    path: str | None = None
    expires: int | None = None
    http_only: bool | None = None
    secure: bool | None = None
    same_site: Literal["Strict", "Lax", "None"] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request."""
        result: dict[str, Any] = {"name": self.name, "value": self.value}
        if self.domain:
            result["domain"] = self.domain
        if self.path:
            result["path"] = self.path
        if self.expires:
            result["expires"] = self.expires
        if self.http_only is not None:
            result["httpOnly"] = self.http_only
        if self.secure is not None:
            result["secure"] = self.secure
        if self.same_site:
            result["sameSite"] = self.same_site
        return result


@dataclass
class HttpAuth:
    """HTTP basic authentication credentials."""
    username: str
    password: str

    def to_dict(self) -> dict[str, Any]:
        return {"username": self.username, "password": self.password}


@dataclass
class ProxyConfig:
    """Proxy configuration."""
    server: str
    username: str | None = None
    password: str | None = None
    bypass: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"server": self.server}
        if self.username:
            result["username"] = self.username
        if self.password:
            result["password"] = self.password
        if self.bypass:
            result["bypass"] = self.bypass
        return result


@dataclass
class Geolocation:
    """Geolocation coordinates for emulation."""
    latitude: float
    longitude: float
    accuracy: float | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"latitude": self.latitude, "longitude": self.longitude}
        if self.accuracy is not None:
            result["accuracy"] = self.accuracy
        return result


@dataclass
class PdfOptions:
    """PDF generation options."""
    page_size: Literal["a4", "a3", "a5", "letter", "legal", "tabloid", "custom"] | None = None
    width: str | None = None
    height: str | None = None
    landscape: bool | None = None
    margin_top: str | None = None
    margin_right: str | None = None
    margin_bottom: str | None = None
    margin_left: str | None = None
    print_background: bool | None = None
    header_template: str | None = None
    footer_template: str | None = None
    display_header_footer: bool | None = None
    scale: float | None = None
    page_ranges: str | None = None
    prefer_css_page_size: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.page_size:
            result["pageSize"] = self.page_size
        if self.width:
            result["width"] = self.width
        if self.height:
            result["height"] = self.height
        if self.landscape is not None:
            result["landscape"] = self.landscape
        if self.margin_top:
            result["marginTop"] = self.margin_top
        if self.margin_right:
            result["marginRight"] = self.margin_right
        if self.margin_bottom:
            result["marginBottom"] = self.margin_bottom
        if self.margin_left:
            result["marginLeft"] = self.margin_left
        if self.print_background is not None:
            result["printBackground"] = self.print_background
        if self.header_template:
            result["headerTemplate"] = self.header_template
        if self.footer_template:
            result["footerTemplate"] = self.footer_template
        if self.display_header_footer is not None:
            result["displayHeaderFooter"] = self.display_header_footer
        if self.scale is not None:
            result["scale"] = self.scale
        if self.page_ranges:
            result["pageRanges"] = self.page_ranges
        if self.prefer_css_page_size is not None:
            result["preferCSSPageSize"] = self.prefer_css_page_size
        return result


@dataclass
class ThumbnailOptions:
    """Thumbnail generation options."""
    enabled: bool = True
    width: int | None = None
    height: int | None = None
    fit: Literal["cover", "contain", "fill"] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"enabled": self.enabled}
        if self.width:
            result["width"] = self.width
        if self.height:
            result["height"] = self.height
        if self.fit:
            result["fit"] = self.fit
        return result


@dataclass
class ExtractMetadata:
    """Options for additional metadata extraction."""
    fonts: bool | None = None
    colors: bool | None = None
    links: bool | None = None
    http_status_code: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.fonts is not None:
            result["fonts"] = self.fonts
        if self.colors is not None:
            result["colors"] = self.colors
        if self.links is not None:
            result["links"] = self.links
        if self.http_status_code is not None:
            result["httpStatusCode"] = self.http_status_code
        return result


@dataclass
class ScreenshotOptions:
    """Options for screenshot capture."""
    url: str | None = None
    html: str | None = None
    markdown: str | None = None
    format: Literal["png", "jpeg", "webp", "avif", "pdf"] = "png"
    quality: int | None = None
    device: DevicePreset | None = None
    width: int = 1280
    height: int = 800
    device_scale_factor: float = 1.0
    is_mobile: bool = False
    has_touch: bool = False
    is_landscape: bool = False
    full_page: bool = False
    full_page_scroll_delay: int | None = None
    full_page_max_height: int | None = None
    selector: str | None = None
    selector_scroll_into_view: bool | None = None
    clip_x: int | None = None
    clip_y: int | None = None
    clip_width: int | None = None
    clip_height: int | None = None
    delay: int = 0
    timeout: int | None = None
    wait_until: Literal["load", "domcontentloaded", "networkidle"] | None = None
    wait_for_selector: str | None = None
    wait_for_selector_timeout: int | None = None
    dark_mode: bool = False
    reduced_motion: bool = False
    css: str | None = None
    javascript: str | None = None
    hide_selectors: list[str] | None = None
    click_selector: str | None = None
    click_delay: int | None = None
    block_ads: bool = False
    block_trackers: bool = False
    block_cookie_banners: bool = False
    block_chat_widgets: bool = False
    block_resources: list[str] | None = None
    user_agent: str | None = None
    extra_headers: dict[str, str] | None = None
    cookies: list[Cookie] | None = None
    http_auth: HttpAuth | None = None
    proxy: ProxyConfig | None = None
    geolocation: Geolocation | None = None
    timezone: str | None = None
    locale: str | None = None
    pdf_options: PdfOptions | None = None
    thumbnail: ThumbnailOptions | None = None
    fail_on_http_error: bool = False
    cache: bool = False
    cache_ttl: int | None = None
    response_type: Literal["binary", "base64", "json"] = "binary"
    include_metadata: bool = False
    extract_metadata: ExtractMetadata | None = None
    fail_if_content_missing: list[str] | None = None
    fail_if_content_contains: list[str] | None = None
    # v2 additions
    storage: dict[str, Any] | None = None  # {destination: 'snapapi'|'user_s3', format?}
    webhook_url: str | None = None         # async delivery
    job_id: str | None = None              # poll async result
    premium_proxy: bool | None = None      # SnapAPI rotating proxy
    # v3 additions
    page_size: str | None = None
    landscape: bool | None = None
    margins: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request."""
        result: dict[str, Any] = {}

        if self.url:
            result["url"] = self.url
        if self.html:
            result["html"] = self.html
        if self.markdown:
            result["markdown"] = self.markdown
        result["format"] = self.format
        if self.quality is not None:
            result["quality"] = self.quality
        if self.device:
            result["device"] = self.device
        result["width"] = self.width
        result["height"] = self.height
        if self.device_scale_factor != 1.0:
            result["deviceScaleFactor"] = self.device_scale_factor
        if self.is_mobile:
            result["isMobile"] = True
        if self.has_touch:
            result["hasTouch"] = True
        if self.is_landscape:
            result["isLandscape"] = True
        if self.full_page:
            result["fullPage"] = True
        if self.full_page_scroll_delay is not None:
            result["fullPageScrollDelay"] = self.full_page_scroll_delay
        if self.full_page_max_height is not None:
            result["fullPageMaxHeight"] = self.full_page_max_height
        if self.selector:
            result["selector"] = self.selector
        if self.selector_scroll_into_view is not None:
            result["selectorScrollIntoView"] = self.selector_scroll_into_view
        if self.clip_x is not None:
            result["clipX"] = self.clip_x
        if self.clip_y is not None:
            result["clipY"] = self.clip_y
        if self.clip_width is not None:
            result["clipWidth"] = self.clip_width
        if self.clip_height is not None:
            result["clipHeight"] = self.clip_height
        if self.delay > 0:
            result["delay"] = self.delay
        if self.timeout is not None:
            result["timeout"] = self.timeout
        if self.wait_until:
            result["waitUntil"] = self.wait_until
        if self.wait_for_selector:
            result["waitForSelector"] = self.wait_for_selector
        if self.wait_for_selector_timeout is not None:
            result["waitForSelectorTimeout"] = self.wait_for_selector_timeout
        if self.dark_mode:
            result["darkMode"] = True
        if self.reduced_motion:
            result["reducedMotion"] = True
        if self.css:
            result["css"] = self.css
        if self.javascript:
            result["javascript"] = self.javascript
        if self.hide_selectors:
            result["hideSelectors"] = self.hide_selectors
        if self.click_selector:
            result["clickSelector"] = self.click_selector
        if self.click_delay is not None:
            result["clickDelay"] = self.click_delay
        if self.block_ads:
            result["blockAds"] = True
        if self.block_trackers:
            result["blockTrackers"] = True
        if self.block_cookie_banners:
            result["blockCookieBanners"] = True
        if self.block_chat_widgets:
            result["blockChatWidgets"] = True
        if self.block_resources:
            result["blockResources"] = self.block_resources
        if self.user_agent:
            result["userAgent"] = self.user_agent
        if self.extra_headers:
            result["extraHeaders"] = self.extra_headers
        if self.cookies:
            result["cookies"] = [c.to_dict() for c in self.cookies]
        if self.http_auth:
            result["httpAuth"] = self.http_auth.to_dict()
        if self.proxy:
            result["proxy"] = self.proxy.to_dict()
        if self.geolocation:
            result["geolocation"] = self.geolocation.to_dict()
        if self.timezone:
            result["timezone"] = self.timezone
        if self.locale:
            result["locale"] = self.locale
        if self.pdf_options:
            result["pdfOptions"] = self.pdf_options.to_dict()
        if self.thumbnail:
            result["thumbnail"] = self.thumbnail.to_dict()
        if self.fail_on_http_error:
            result["failOnHttpError"] = True
        if self.cache:
            result["cache"] = True
        if self.cache_ttl is not None:
            result["cacheTtl"] = self.cache_ttl
        if self.response_type != "binary":
            result["responseType"] = self.response_type
        if self.include_metadata:
            result["includeMetadata"] = True
        if self.extract_metadata:
            result["extractMetadata"] = self.extract_metadata.to_dict()
        if self.fail_if_content_missing:
            result["failIfContentMissing"] = self.fail_if_content_missing
        if self.fail_if_content_contains:
            result["failIfContentContains"] = self.fail_if_content_contains
        if self.storage is not None:
            result["storage"] = self.storage
        if self.webhook_url:
            result["webhookUrl"] = self.webhook_url
        if self.job_id:
            result["jobId"] = self.job_id
        if self.premium_proxy is not None:
            result["premiumProxy"] = self.premium_proxy
        if self.block_trackers:
            result["blockTrackers"] = True
        if self.block_chat_widgets:
            result["blockChatWidgets"] = True
        if self.page_size:
            result["pageSize"] = self.page_size
        if self.landscape is not None:
            result["landscape"] = self.landscape
        if self.margins:
            result["margins"] = self.margins

        return result


@dataclass
class ScreenshotMetadata:
    """Page metadata from screenshot."""
    title: str | None = None
    description: str | None = None
    favicon: str | None = None
    og_title: str | None = None
    og_description: str | None = None
    og_image: str | None = None
    http_status_code: int | None = None
    fonts: list[str] | None = None
    colors: list[str] | None = None
    links: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScreenshotMetadata:
        return cls(
            title=data.get("title"),
            description=data.get("description"),
            favicon=data.get("favicon"),
            og_title=data.get("ogTitle"),
            og_description=data.get("ogDescription"),
            og_image=data.get("ogImage"),
            http_status_code=data.get("httpStatusCode"),
            fonts=data.get("fonts"),
            colors=data.get("colors"),
            links=data.get("links"),
        )


@dataclass
class ScreenshotResult:
    """Result of a screenshot capture."""
    success: bool
    format: str
    width: int
    height: int
    file_size: int
    took: int
    cached: bool
    data: str | None = None
    metadata: ScreenshotMetadata | None = None
    thumbnail: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScreenshotResult:
        """Create from API response dictionary."""
        metadata = None
        if data.get("metadata"):
            metadata = ScreenshotMetadata.from_dict(data["metadata"])

        return cls(
            success=data.get("success", False),
            format=data.get("format", "png"),
            width=data.get("width", 0),
            height=data.get("height", 0),
            file_size=data.get("fileSize", 0),
            took=data.get("took", 0),
            cached=data.get("cached", False),
            data=data.get("data"),
            metadata=metadata,
            thumbnail=data.get("thumbnail"),
        )


ScrollEasing = Literal["linear", "ease_in", "ease_out", "ease_in_out", "ease_in_out_quint"]


@dataclass
class VideoOptions:
    """Options for video capture."""
    url: str
    format: Literal["mp4", "webm", "gif"] = "mp4"
    quality: int | None = None
    width: int = 1280
    height: int = 720
    device: DevicePreset | None = None
    duration: int = 5
    fps: int = 24
    delay: int = 0
    timeout: int = 60000
    wait_until: Literal["load", "domcontentloaded", "networkidle"] | None = None
    wait_for_selector: str | None = None
    dark_mode: bool = False
    block_ads: bool = False
    block_cookie_banners: bool = False
    css: str | None = None
    javascript: str | None = None
    hide_selectors: list[str] | None = None
    user_agent: str | None = None
    cookies: list[Cookie] | None = None
    response_type: Literal["binary", "base64", "json"] = "binary"
    scrolling: bool = False
    scroll_speed: int | None = None
    scroll_delay: int | None = None
    scroll_duration: int | None = None
    scroll_by: int | None = None
    scroll_easing: ScrollEasing | None = None
    scroll_back: bool = True
    scroll_complete: bool = True
    # Legacy compat alias (v2 used `scroll`, v3 uses `scrolling`)
    scroll: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request."""
        result: dict[str, Any] = {
            "url": self.url,
            "format": self.format,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "fps": self.fps,
        }
        if self.quality is not None:
            result["quality"] = self.quality
        if self.device:
            result["device"] = self.device
        if self.delay > 0:
            result["delay"] = self.delay
        if self.timeout != 60000:
            result["timeout"] = self.timeout
        if self.wait_until:
            result["waitUntil"] = self.wait_until
        if self.wait_for_selector:
            result["waitForSelector"] = self.wait_for_selector
        if self.dark_mode:
            result["darkMode"] = True
        if self.block_ads:
            result["blockAds"] = True
        if self.block_cookie_banners:
            result["blockCookieBanners"] = True
        if self.css:
            result["css"] = self.css
        if self.javascript:
            result["javascript"] = self.javascript
        if self.hide_selectors:
            result["hideSelectors"] = self.hide_selectors
        if self.user_agent:
            result["userAgent"] = self.user_agent
        if self.cookies:
            result["cookies"] = [c.to_dict() for c in self.cookies]
        if self.scrolling or self.scroll:
            result["scrolling"] = True
        if self.scroll_speed is not None:
            result["scrollSpeed"] = self.scroll_speed
        if self.scroll_delay is not None:
            result["scrollDelay"] = self.scroll_delay
        if self.scroll_duration is not None:
            result["scrollDuration"] = self.scroll_duration
        if self.scroll_by is not None:
            result["scrollBy"] = self.scroll_by
        if self.scroll_easing:
            result["scrollEasing"] = self.scroll_easing
        if self.scroll_back:
            result["scrollBack"] = True
        if self.scroll_complete:
            result["scrollComplete"] = True
        return result


@dataclass
class VideoResult:
    """Result of a video capture."""
    success: bool
    format: str
    width: int
    height: int
    file_size: int
    duration: int
    took: int
    data: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VideoResult:
        """Create from API response dictionary."""
        return cls(
            success=data.get("success", False),
            format=data.get("format", "mp4"),
            width=data.get("width", 0),
            height=data.get("height", 0),
            file_size=data.get("fileSize", 0),
            duration=data.get("duration", 0),
            took=data.get("took", 0),
            data=data.get("data"),
        )


@dataclass
class BatchOptions:
    """Options for batch screenshot capture."""
    urls: list[str]
    format: Literal["png", "jpeg", "webp", "avif", "pdf"] = "png"
    quality: int | None = None
    width: int = 1280
    height: int = 800
    full_page: bool = False
    webhook_url: str | None = None
    dark_mode: bool = False
    block_ads: bool = False
    block_cookie_banners: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request."""
        result: dict[str, Any] = {
            "urls": self.urls,
            "format": self.format,
            "width": self.width,
            "height": self.height,
        }

        if self.quality is not None:
            result["quality"] = self.quality
        if self.full_page:
            result["fullPage"] = True
        if self.webhook_url:
            result["webhookUrl"] = self.webhook_url
        if self.dark_mode:
            result["darkMode"] = True
        if self.block_ads:
            result["blockAds"] = True
        if self.block_cookie_banners:
            result["blockCookieBanners"] = True

        return result


@dataclass
class BatchResultItem:
    """Individual result in a batch job."""
    url: str
    status: Literal["pending", "completed", "failed"]
    data: str | None = None
    error: str | None = None
    duration: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BatchResultItem:
        return cls(
            url=data.get("url", ""),
            status=data.get("status", "pending"),
            data=data.get("data"),
            error=data.get("error"),
            duration=data.get("duration"),
        )


@dataclass
class BatchResult:
    """Result of a batch screenshot job."""
    success: bool
    job_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    total: int
    completed: int | None = None
    failed: int | None = None
    results: list[BatchResultItem] | None = None
    created_at: str | None = None
    completed_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BatchResult:
        """Create from API response dictionary."""
        results = None
        if data.get("results"):
            results = [BatchResultItem.from_dict(r) for r in data["results"]]

        return cls(
            success=data.get("success", False),
            job_id=data.get("jobId", ""),
            status=data.get("status", "processing"),
            total=data.get("total", 0),
            completed=data.get("completed"),
            failed=data.get("failed"),
            results=results,
            created_at=data.get("createdAt"),
            completed_at=data.get("completedAt"),
        )


@dataclass
class DeviceInfo:
    """Device preset information."""
    id: str
    name: str
    width: int
    height: int
    device_scale_factor: float
    is_mobile: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeviceInfo:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            width=data.get("width", 0),
            height=data.get("height", 0),
            device_scale_factor=data.get("deviceScaleFactor", 1),
            is_mobile=data.get("isMobile", False),
        )


@dataclass
class DevicesResult:
    """Result of get_devices call."""
    success: bool
    devices: dict[str, list[DeviceInfo]]
    total: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DevicesResult:
        devices = {}
        for category, device_list in data.get("devices", {}).items():
            devices[category] = [DeviceInfo.from_dict(d) for d in device_list]
        return cls(
            success=data.get("success", False),
            devices=devices,
            total=data.get("total", 0),
        )


@dataclass
class CapabilitiesResult:
    """Result of get_capabilities call."""
    success: bool
    version: str
    capabilities: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CapabilitiesResult:
        return cls(
            success=data.get("success", False),
            version=data.get("version", ""),
            capabilities=data.get("capabilities", {}),
        )


@dataclass
class UsageResult:
    """Result of get_usage call."""
    used: int
    limit: int
    remaining: int
    reset_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UsageResult:
        return cls(
            used=data.get("used", 0),
            limit=data.get("limit", 0),
            remaining=data.get("remaining", 0),
            reset_at=data.get("resetAt", ""),
        )


# Extract type
ExtractType = Literal[
    "markdown", "text", "html", "article", "structured",
    "links", "images", "metadata",
]


ScrapeType = Literal["text", "html", "links"]


@dataclass
class ScrapeOptions:
    """Options for multi-page web scraping."""
    url: str
    pages: int = 1
    type: ScrapeType = "text"
    wait_ms: int | None = None
    proxy: str | None = None
    premium_proxy: bool | None = None
    block_resources: bool = False
    page_step: int | None = None
    locale: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request."""
        result: dict[str, Any] = {
            "url": self.url,
            "pages": self.pages,
            "type": self.type,
        }
        if self.wait_ms is not None:
            result["waitMs"] = self.wait_ms
        if self.proxy:
            result["proxy"] = self.proxy
        if self.premium_proxy is not None:
            result["premiumProxy"] = self.premium_proxy
        if self.block_resources:
            result["blockResources"] = True
        if self.page_step is not None:
            result["pageStep"] = self.page_step
        if self.locale:
            result["locale"] = self.locale
        return result


@dataclass
class ScrapePageResult:
    """A single scraped page result."""
    page: int
    url: str
    data: str


@dataclass
class ScrapeResult:
    """Result of a multi-page scrape."""
    success: bool
    results: list[ScrapePageResult]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScrapeResult:
        """Create from API response dictionary."""
        results = [
            ScrapePageResult(page=r["page"], url=r["url"], data=r["data"])
            for r in data.get("results", [])
        ]
        return cls(success=data.get("success", False), results=results)


@dataclass
class ExtractOptions:
    """Options for content extraction."""
    url: str
    type: ExtractType = "markdown"
    selector: str | None = None
    wait_for: str | None = None
    timeout: int | None = None
    dark_mode: bool = False
    block_ads: bool = False
    block_cookie_banners: bool = False
    include_images: bool | None = None
    max_length: int | None = None
    clean_output: bool | None = None
    proxy: str | None = None
    block_resources: bool = False
    locale: str | None = None
    user_agent: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request."""
        result: dict[str, Any] = {
            "url": self.url,
            "type": self.type,
        }
        if self.selector:
            result["selector"] = self.selector
        if self.wait_for:
            result["waitFor"] = self.wait_for
        if self.timeout is not None:
            result["timeout"] = self.timeout
        if self.dark_mode:
            result["darkMode"] = True
        if self.block_ads:
            result["blockAds"] = True
        if self.block_cookie_banners:
            result["blockCookieBanners"] = True
        if self.include_images is not None:
            result["includeImages"] = self.include_images
        if self.max_length is not None:
            result["maxLength"] = self.max_length
        if self.clean_output is not None:
            result["cleanOutput"] = self.clean_output
        if self.proxy:
            result["proxy"] = self.proxy
        if self.block_resources:
            result["blockResources"] = True
        if self.locale:
            result["locale"] = self.locale
        if self.user_agent:
            result["userAgent"] = self.user_agent
        return result


@dataclass
class ExtractResult:
    """Result of a content extraction."""
    success: bool
    type: str
    content: Any | None = None
    url: str | None = None
    title: str | None = None
    took: int | None = None
    cached: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExtractResult:
        """Create from API response dictionary."""
        return cls(
            success=data.get("success", False),
            type=data.get("type", ""),
            # API returns extracted content in "data" field; fall back to "content" for compat
            content=data.get("data", data.get("content")),
            url=data.get("url"),
            title=data.get("title"),
            # API returns timing as "took" (preferred) or "responseTime" (legacy alias)
            took=data.get("took", data.get("responseTime")),
            cached=data.get("cached", False),
        )


# Analyze provider type
AnalyzeProvider = Literal["openai", "anthropic"]


@dataclass
class AnalyzeOptions:
    """Options for AI-powered page analysis."""
    url: str
    prompt: str
    provider: AnalyzeProvider | None = None
    api_key: str | None = None
    model: str | None = None
    json_schema: dict[str, Any] | None = None
    timeout: int | None = None
    wait_for: str | None = None
    block_ads: bool = False
    block_cookie_banners: bool = False
    include_screenshot: bool | None = None
    include_metadata: bool | None = None
    max_content_length: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request."""
        result: dict[str, Any] = {
            "url": self.url,
            "prompt": self.prompt,
        }
        if self.provider:
            result["provider"] = self.provider
        if self.api_key:
            result["apiKey"] = self.api_key
        if self.model:
            result["model"] = self.model
        if self.json_schema is not None:
            result["jsonSchema"] = self.json_schema
        if self.timeout is not None:
            result["timeout"] = self.timeout
        if self.wait_for:
            result["waitFor"] = self.wait_for
        if self.block_ads:
            result["blockAds"] = True
        if self.block_cookie_banners:
            result["blockCookieBanners"] = True
        if self.include_screenshot is not None:
            result["includeScreenshot"] = self.include_screenshot
        if self.include_metadata is not None:
            result["includeMetadata"] = self.include_metadata
        if self.max_content_length is not None:
            result["maxContentLength"] = self.max_content_length
        return result


@dataclass
class AnalyzeResult:
    """Result of an AI-powered page analysis."""
    success: bool
    result: Any | None = None
    url: str | None = None
    model: str | None = None
    provider: str | None = None
    took: int | None = None
    tokens_used: int | None = None
    screenshot: str | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnalyzeResult:
        """Create from API response dictionary."""
        return cls(
            success=data.get("success", False),
            # API returns LLM output in "analysis" field; fall back to "result" for compat
            result=data.get("analysis", data.get("result")),
            url=data.get("url"),
            model=data.get("model"),
            provider=data.get("provider"),
            # API returns timing as "took" (preferred) or "responseTime" (legacy alias)
            took=data.get("took", data.get("responseTime")),
            tokens_used=data.get("tokensUsed"),
            screenshot=data.get("screenshot"),
            metadata=data.get("metadata"),
        )


# ─────────────────────────────────────────────
# Storage Types (v2)
# ─────────────────────────────────────────────

@dataclass
class StorageFile:
    """A file stored in SnapAPI cloud or user S3."""
    id: str
    url: str
    filename: str | None = None
    size: int | None = None
    format: str | None = None
    created_at: str | None = None
    extra: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StorageFile:
        known = {"id", "url", "filename", "size", "format", "createdAt"}
        return cls(
            id=data["id"],
            url=data["url"],
            filename=data.get("filename"),
            size=data.get("size"),
            format=data.get("format"),
            created_at=data.get("createdAt"),
            extra={k: v for k, v in data.items() if k not in known},
        )


@dataclass
class StorageListResult:
    """Result of listing stored files."""
    files: list[StorageFile]
    total: int | None = None
    limit: int | None = None
    offset: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StorageListResult:
        files = [StorageFile.from_dict(f) for f in data.get("files", [])]
        return cls(
            files=files,
            total=data.get("total"),
            limit=data.get("limit"),
            offset=data.get("offset"),
        )


@dataclass
class StorageUsage:
    """Storage usage info for the current account."""
    used: int
    limit: int
    percentage: float
    used_formatted: str
    limit_formatted: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StorageUsage:
        return cls(
            used=data.get("used", 0),
            limit=data.get("limit", 0),
            percentage=data.get("percentage", 0.0),
            used_formatted=data.get("usedFormatted", ""),
            limit_formatted=data.get("limitFormatted", ""),
        )


@dataclass
class S3Config:
    """Custom S3-compatible storage configuration."""
    s3_bucket: str
    s3_region: str
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_endpoint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "s3_bucket": self.s3_bucket,
            "s3_region": self.s3_region,
            "s3_access_key_id": self.s3_access_key_id,
            "s3_secret_access_key": self.s3_secret_access_key,
        }
        if self.s3_endpoint:
            result["s3_endpoint"] = self.s3_endpoint
        return result


@dataclass
class S3TestResult:
    """Result of testing the S3 connection."""
    success: bool
    message: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> S3TestResult:
        return cls(success=data.get("success", False), message=data.get("message"))


@dataclass
class DeleteResult:
    """Generic delete result."""
    success: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeleteResult:
        return cls(success=data.get("success", False))


# ─────────────────────────────────────────────
# Scheduled Screenshot Types (v2)
# ─────────────────────────────────────────────

@dataclass
class CreateScheduledOptions:
    """Options for creating a scheduled screenshot job."""
    url: str
    cron_expression: str
    format: str | None = None
    width: int | None = None
    height: int | None = None
    full_page: bool | None = None
    webhook_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "url": self.url,
            "cronExpression": self.cron_expression,
        }
        if self.format:
            result["format"] = self.format
        if self.width is not None:
            result["width"] = self.width
        if self.height is not None:
            result["height"] = self.height
        if self.full_page is not None:
            result["fullPage"] = self.full_page
        if self.webhook_url:
            result["webhookUrl"] = self.webhook_url
        return result


@dataclass
class ScheduledScreenshot:
    """A scheduled screenshot job."""
    id: str
    url: str
    cron_expression: str
    next_run: str | None = None
    format: str | None = None
    width: int | None = None
    height: int | None = None
    full_page: bool | None = None
    webhook_url: str | None = None
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScheduledScreenshot:
        return cls(
            id=data["id"],
            url=data["url"],
            cron_expression=data.get("cronExpression", ""),
            next_run=data.get("nextRun"),
            format=data.get("format"),
            width=data.get("width"),
            height=data.get("height"),
            full_page=data.get("fullPage"),
            webhook_url=data.get("webhookUrl"),
            created_at=data.get("createdAt"),
        )


# ─────────────────────────────────────────────
# Webhook Types (v2)
# ─────────────────────────────────────────────

@dataclass
class CreateWebhookOptions:
    """Options for registering a webhook."""
    url: str
    events: list[str]
    secret: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"url": self.url, "events": self.events}
        if self.secret:
            result["secret"] = self.secret
        return result


@dataclass
class Webhook:
    """A registered webhook endpoint."""
    id: str
    url: str
    events: list[str]
    secret: str | None = None
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Webhook:
        return cls(
            id=data["id"],
            url=data["url"],
            events=data.get("events", []),
            secret=data.get("secret"),
            created_at=data.get("createdAt"),
        )


# ─────────────────────────────────────────────
# API Key Types (v2)
# ─────────────────────────────────────────────

@dataclass
class ApiKey:
    """An API key (value is masked in list responses)."""
    id: str
    name: str
    key: str
    created_at: str | None = None
    last_used: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ApiKey:
        return cls(
            id=data["id"],
            name=data["name"],
            key=data.get("key", ""),
            created_at=data.get("createdAt"),
            last_used=data.get("lastUsed"),
        )


@dataclass
class CreateApiKeyResult:
    """Result of creating a new API key (full key shown only once)."""
    id: str
    name: str
    key: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateApiKeyResult:
        return cls(id=data["id"], name=data["name"], key=data["key"])
