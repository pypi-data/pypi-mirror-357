"""
Endpoints API models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from ..base import AIRBaseModel, Filter


class TagType(str, Enum):
    """Endpoint tag types."""
    SYSTEM = "system"
    USER = "user"
    CUSTOM = "custom"
    AUTO = "auto"


class TagScope(str, Enum):
    """Tag scope."""
    GLOBAL = "global"
    ORGANIZATION = "organization"
    GROUP = "group"


class EndpointTag(AIRBaseModel):
    """Endpoint tag model."""
    
    id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    tag_type: TagType = TagType.USER
    scope: TagScope = TagScope.ORGANIZATION
    organization_id: Optional[int] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    usage_count: int = 0
    is_system: bool = False
    is_deletable: bool = True
    metadata: Optional[Dict[str, Any]] = None
    rules: Optional[Dict[str, Any]] = None  # Auto-tagging rules


class CreateEndpointTagRequest(AIRBaseModel):
    """Request model for creating endpoint tags."""
    
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    tag_type: TagType = TagType.USER
    scope: TagScope = TagScope.ORGANIZATION
    organization_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    rules: Optional[Dict[str, Any]] = None


class UpdateEndpointTagRequest(AIRBaseModel):
    """Request model for updating endpoint tags."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    rules: Optional[Dict[str, Any]] = None


class EndpointTagFilter(Filter):
    """Filter for endpoint tag queries."""
    
    name: Optional[str] = None
    tag_type: Optional[TagType] = None
    scope: Optional[TagScope] = None
    created_by: Optional[str] = None 