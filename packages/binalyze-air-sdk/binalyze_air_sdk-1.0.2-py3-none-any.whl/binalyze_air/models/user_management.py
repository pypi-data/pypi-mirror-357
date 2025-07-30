"""
User Management-related data models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from ..base import AIRBaseModel, Filter


class UserManagementUser(AIRBaseModel):
    """User management user model."""
    
    id: str
    username: str
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    organizationId: int
    role: Optional[str] = None
    isActive: bool = True
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


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


class AIUser(AIRBaseModel):
    """AI user model."""
    
    id: str
    name: str
    description: Optional[str] = None
    capabilities: List[str] = []
    organizationId: int
    isActive: bool = True


class CreateAIUserRequest(AIRBaseModel):
    """Create AI user request model."""
    
    name: str
    description: Optional[str] = None
    capabilities: List[str] = []
    organizationId: int


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