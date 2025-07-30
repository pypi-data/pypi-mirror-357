"""
Settings API models for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel


class BannerType(str, Enum):
    """Banner types."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    MAINTENANCE = "maintenance"


class BannerPosition(str, Enum):
    """Banner display positions."""
    TOP = "top"
    BOTTOM = "bottom"
    CENTER = "center"


class BannerSettings(AIRBaseModel):
    """Banner settings model."""
    
    id: Optional[str] = None
    enabled: bool = False
    title: Optional[str] = None
    message: str
    banner_type: BannerType = BannerType.INFO
    position: BannerPosition = BannerPosition.TOP
    dismissible: bool = True
    auto_dismiss: bool = False
    auto_dismiss_timeout: Optional[int] = None  # seconds
    show_from: Optional[datetime] = None
    show_until: Optional[datetime] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    icon: Optional[str] = None
    link_url: Optional[str] = None
    link_text: Optional[str] = None
    target_roles: Optional[list[str]] = None
    target_organizations: Optional[list[int]] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    organization_id: Optional[int] = None


class UpdateBannerSettingsRequest(AIRBaseModel):
    """Request model for updating banner settings with proper API field mapping."""
    
    enabled: Optional[bool] = None
    title: Optional[str] = None
    message: Optional[str] = None
    # API expects these exact field names - use aliases to map from Python names to API names
    users_can_dismiss: Optional[bool] = Field(default=None, alias="usersCanDismiss")
    color: Optional[str] = None  # API expects: general, info, maintenance, warning, alert
    display_time_type: Optional[str] = Field(default=None, alias="displayTimeType")  # always or scheduled
    schedule_times: Optional[Dict[str, Any]] = Field(default=None, alias="scheduleTimes")
    
    # Legacy/additional fields (may not be used by current API)
    banner_type: Optional[BannerType] = None
    position: Optional[BannerPosition] = None
    dismissible: Optional[bool] = None
    auto_dismiss: Optional[bool] = None
    auto_dismiss_timeout: Optional[int] = None
    show_from: Optional[datetime] = None
    show_until: Optional[datetime] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    icon: Optional[str] = None
    link_url: Optional[str] = None
    link_text: Optional[str] = None
    target_roles: Optional[list[str]] = None
    target_organizations: Optional[list[int]] = None 