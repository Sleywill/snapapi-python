"""
Type definitions for SnapAPI Python SDK
"""

from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field


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
class ScreenshotOptions:
    """Options for screenshot capture."""
    url: str
    format: Literal["png", "jpeg", "webp", "pdf"] = "png"
    width: int = 1920
    height: int = 1080
    full_page: bool = False
    quality: Optional[int] = None
    scale: float = 1.0
    delay: int = 0
    timeout: int = 30000
    dark_mode: bool = False
    mobile: bool = False
    selector: Optional[str] = None
    wait_for_selector: Optional[str] = None
    javascript: Optional[str] = None
    block_ads: bool = False
    hide_cookie_banners: bool = False
    cookies: Optional[List[Cookie]] = None
    headers: Optional[Dict[str, str]] = None
    response_type: Literal["binary", "base64", "json"] = "binary"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        result = {
            "url": self.url,
            "format": self.format,
            "width": self.width,
            "height": self.height,
        }

        if self.full_page:
            result["fullPage"] = True
        if self.quality is not None:
            result["quality"] = self.quality
        if self.scale != 1.0:
            result["scale"] = self.scale
        if self.delay > 0:
            result["delay"] = self.delay
        if self.timeout != 30000:
            result["timeout"] = self.timeout
        if self.dark_mode:
            result["darkMode"] = True
        if self.mobile:
            result["mobile"] = True
        if self.selector:
            result["selector"] = self.selector
        if self.wait_for_selector:
            result["waitForSelector"] = self.wait_for_selector
        if self.javascript:
            result["javascript"] = self.javascript
        if self.block_ads:
            result["blockAds"] = True
        if self.hide_cookie_banners:
            result["hideCookieBanners"] = True
        if self.cookies:
            result["cookies"] = [c.to_dict() for c in self.cookies]
        if self.headers:
            result["headers"] = self.headers
        if self.response_type != "binary":
            result["responseType"] = self.response_type

        return result


@dataclass
class ScreenshotResult:
    """Result of a screenshot capture."""
    success: bool
    format: str
    width: int
    height: int
    file_size: int
    duration: int
    cached: bool
    data: Optional[str] = None  # Base64 encoded when response_type is json

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScreenshotResult":
        """Create from API response dictionary."""
        return cls(
            success=data.get("success", False),
            format=data.get("format", "png"),
            width=data.get("width", 0),
            height=data.get("height", 0),
            file_size=data.get("fileSize", 0),
            duration=data.get("duration", 0),
            cached=data.get("cached", False),
            data=data.get("data"),
        )


@dataclass
class BatchOptions:
    """Options for batch screenshot capture."""
    urls: List[str]
    format: Literal["png", "jpeg", "webp", "pdf"] = "png"
    width: int = 1920
    height: int = 1080
    full_page: bool = False
    webhook_url: Optional[str] = None
    dark_mode: bool = False
    block_ads: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        result = {
            "urls": self.urls,
            "format": self.format,
            "width": self.width,
            "height": self.height,
        }

        if self.full_page:
            result["fullPage"] = True
        if self.webhook_url:
            result["webhookUrl"] = self.webhook_url
        if self.dark_mode:
            result["darkMode"] = True
        if self.block_ads:
            result["blockAds"] = True

        return result


@dataclass
class BatchResult:
    """Result of a batch screenshot job."""
    job_id: str
    status: Literal["processing", "completed", "failed"]
    estimated_time: Optional[int] = None
    results: Optional[List[ScreenshotResult]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchResult":
        """Create from API response dictionary."""
        results = None
        if data.get("results"):
            results = [ScreenshotResult.from_dict(r) for r in data["results"]]

        return cls(
            job_id=data.get("jobId", ""),
            status=data.get("status", "processing"),
            estimated_time=data.get("estimatedTime"),
            results=results,
        )
