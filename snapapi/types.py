"""
Type definitions for SnapAPI Python SDK
"""

from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field


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
    domain: Optional[str] = None
    path: Optional[str] = None
    expires: Optional[int] = None
    http_only: Optional[bool] = None
    secure: Optional[bool] = None
    same_site: Optional[Literal["Strict", "Lax", "None"]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        result = {"name": self.name, "value": self.value}
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

    def to_dict(self) -> Dict[str, Any]:
        return {"username": self.username, "password": self.password}


@dataclass
class ProxyConfig:
    """Proxy configuration."""
    server: str
    username: Optional[str] = None
    password: Optional[str] = None
    bypass: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"server": self.server}
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
    accuracy: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"latitude": self.latitude, "longitude": self.longitude}
        if self.accuracy is not None:
            result["accuracy"] = self.accuracy
        return result


@dataclass
class PdfOptions:
    """PDF generation options."""
    page_size: Optional[Literal["a4", "a3", "a5", "letter", "legal", "tabloid", "custom"]] = None
    width: Optional[str] = None
    height: Optional[str] = None
    landscape: Optional[bool] = None
    margin_top: Optional[str] = None
    margin_right: Optional[str] = None
    margin_bottom: Optional[str] = None
    margin_left: Optional[str] = None
    print_background: Optional[bool] = None
    header_template: Optional[str] = None
    footer_template: Optional[str] = None
    display_header_footer: Optional[bool] = None
    scale: Optional[float] = None
    page_ranges: Optional[str] = None
    prefer_css_page_size: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
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
    width: Optional[int] = None
    height: Optional[int] = None
    fit: Optional[Literal["cover", "contain", "fill"]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"enabled": self.enabled}
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
    fonts: Optional[bool] = None
    colors: Optional[bool] = None
    links: Optional[bool] = None
    http_status_code: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
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
    url: Optional[str] = None
    html: Optional[str] = None
    markdown: Optional[str] = None
    format: Literal["png", "jpeg", "webp", "avif", "pdf"] = "png"
    quality: Optional[int] = None
    device: Optional[DevicePreset] = None
    width: int = 1280
    height: int = 800
    device_scale_factor: float = 1.0
    is_mobile: bool = False
    has_touch: bool = False
    is_landscape: bool = False
    full_page: bool = False
    full_page_scroll_delay: Optional[int] = None
    full_page_max_height: Optional[int] = None
    selector: Optional[str] = None
    selector_scroll_into_view: Optional[bool] = None
    clip_x: Optional[int] = None
    clip_y: Optional[int] = None
    clip_width: Optional[int] = None
    clip_height: Optional[int] = None
    delay: int = 0
    timeout: int = 30000
    wait_until: Optional[Literal["load", "domcontentloaded", "networkidle"]] = None
    wait_for_selector: Optional[str] = None
    wait_for_selector_timeout: Optional[int] = None
    dark_mode: bool = False
    reduced_motion: bool = False
    css: Optional[str] = None
    javascript: Optional[str] = None
    hide_selectors: Optional[List[str]] = None
    click_selector: Optional[str] = None
    click_delay: Optional[int] = None
    block_ads: bool = False
    block_trackers: bool = False
    block_cookie_banners: bool = False
    block_chat_widgets: bool = False
    block_resources: Optional[List[str]] = None
    user_agent: Optional[str] = None
    extra_headers: Optional[Dict[str, str]] = None
    cookies: Optional[List[Cookie]] = None
    http_auth: Optional[HttpAuth] = None
    proxy: Optional[ProxyConfig] = None
    geolocation: Optional[Geolocation] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    pdf_options: Optional[PdfOptions] = None
    thumbnail: Optional[ThumbnailOptions] = None
    fail_on_http_error: bool = False
    cache: bool = False
    cache_ttl: Optional[int] = None
    response_type: Literal["binary", "base64", "json"] = "binary"
    include_metadata: bool = False
    extract_metadata: Optional[ExtractMetadata] = None
    fail_if_content_missing: Optional[List[str]] = None
    fail_if_content_contains: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        result = {}

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
        if self.timeout != 30000:
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

        return result


@dataclass
class ScreenshotMetadata:
    """Page metadata from screenshot."""
    title: Optional[str] = None
    description: Optional[str] = None
    favicon: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    http_status_code: Optional[int] = None
    fonts: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    links: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScreenshotMetadata":
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
    data: Optional[str] = None
    metadata: Optional[ScreenshotMetadata] = None
    thumbnail: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScreenshotResult":
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
    quality: Optional[int] = None
    width: int = 1280
    height: int = 720
    device: Optional[DevicePreset] = None
    duration: int = 5000
    fps: int = 24
    delay: int = 0
    timeout: int = 60000
    wait_until: Optional[Literal["load", "domcontentloaded", "networkidle"]] = None
    wait_for_selector: Optional[str] = None
    dark_mode: bool = False
    block_ads: bool = False
    block_cookie_banners: bool = False
    css: Optional[str] = None
    javascript: Optional[str] = None
    hide_selectors: Optional[List[str]] = None
    user_agent: Optional[str] = None
    cookies: Optional[List[Cookie]] = None
    response_type: Literal["binary", "base64", "json"] = "binary"
    scroll: bool = False
    scroll_delay: Optional[int] = None
    scroll_duration: Optional[int] = None
    scroll_by: Optional[int] = None
    scroll_easing: Optional[ScrollEasing] = None
    scroll_back: bool = False
    scroll_complete: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        result = {
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
        if self.response_type != "binary":
            result["responseType"] = self.response_type
        if self.scroll:
            result["scroll"] = True
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
    data: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VideoResult":
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
    urls: List[str]
    format: Literal["png", "jpeg", "webp", "avif", "pdf"] = "png"
    quality: Optional[int] = None
    width: int = 1280
    height: int = 800
    full_page: bool = False
    webhook_url: Optional[str] = None
    dark_mode: bool = False
    block_ads: bool = False
    block_cookie_banners: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        result = {
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
    data: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchResultItem":
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
    completed: Optional[int] = None
    failed: Optional[int] = None
    results: Optional[List[BatchResultItem]] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchResult":
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
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceInfo":
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
    devices: Dict[str, List[DeviceInfo]]
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DevicesResult":
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
    capabilities: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CapabilitiesResult":
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
    def from_dict(cls, data: Dict[str, Any]) -> "UsageResult":
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


@dataclass
class ExtractOptions:
    """Options for content extraction."""
    url: str
    type: ExtractType = "markdown"
    selector: Optional[str] = None
    wait_for: Optional[str] = None
    timeout: Optional[int] = None
    dark_mode: bool = False
    block_ads: bool = False
    block_cookie_banners: bool = False
    include_images: Optional[bool] = None
    max_length: Optional[int] = None
    clean_output: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        result: Dict[str, Any] = {
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
        return result


@dataclass
class ExtractResult:
    """Result of a content extraction."""
    success: bool
    type: str
    content: Optional[Any] = None
    url: Optional[str] = None
    title: Optional[str] = None
    took: Optional[int] = None
    cached: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractResult":
        """Create from API response dictionary."""
        return cls(
            success=data.get("success", False),
            type=data.get("type", ""),
            content=data.get("content"),
            url=data.get("url"),
            title=data.get("title"),
            took=data.get("took"),
            cached=data.get("cached", False),
        )


# Analyze provider type
AnalyzeProvider = Literal["openai", "anthropic"]


@dataclass
class AnalyzeOptions:
    """Options for AI-powered page analysis."""
    url: str
    prompt: str
    provider: Optional[AnalyzeProvider] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    json_schema: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None
    wait_for: Optional[str] = None
    block_ads: bool = False
    block_cookie_banners: bool = False
    include_screenshot: Optional[bool] = None
    include_metadata: Optional[bool] = None
    max_content_length: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        result: Dict[str, Any] = {
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
    result: Optional[Any] = None
    url: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    took: Optional[int] = None
    tokens_used: Optional[int] = None
    screenshot: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalyzeResult":
        """Create from API response dictionary."""
        return cls(
            success=data.get("success", False),
            result=data.get("result"),
            url=data.get("url"),
            model=data.get("model"),
            provider=data.get("provider"),
            took=data.get("took"),
            tokens_used=data.get("tokensUsed"),
            screenshot=data.get("screenshot"),
            metadata=data.get("metadata"),
        )
