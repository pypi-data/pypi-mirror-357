"""
Users-related data models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import Field

from ..base import AIRBaseModel, Filter


class User(AIRBaseModel):
    """User model."""
    
    id: str = Field(alias="_id")
    username: str
    email: str
    organization_ids: Optional[Union[List[int], str]] = Field(default=None, alias="organizationIds")
    strategy: Optional[str] = None
    profile: Optional[Dict[str, str]] = None
    tfa_enabled: Optional[bool] = Field(default=False, alias="tfaEnabled")
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    organization_id: Optional[int] = Field(default=None, alias="organizationId")
    role: Optional[str] = None
    is_active: bool = Field(default=True, alias="isActive")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")


class CreateUserRequest(AIRBaseModel):
    """Create user request model."""
    
    username: str
    email: str
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    organizationId: int
    role: Optional[str] = None


class UpdateUserRequest(AIRBaseModel):
    """Update user request model."""
    
    username: Optional[str] = None
    email: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: Optional[str] = None
    isActive: Optional[bool] = None


class APIUser(AIRBaseModel):
    """API user model."""
    
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    organizationId: int
    apiKey: Optional[str] = None
    isActive: bool = True


class CreateAPIUserRequest(AIRBaseModel):
    """Create API user request model."""
    
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    organizationId: int


class UserFilter(Filter):
    """Filter for user queries."""
    
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    organizationId: Optional[int] = None
    isActive: Optional[bool] = None 