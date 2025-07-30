"""
Auto Asset Tags-related data models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from pydantic import ConfigDict

from ..base import AIRBaseModel, Filter


class AutoAssetTag(AIRBaseModel):
    """Auto asset tag model."""
    
    id: str = Field(alias="_id")
    tag: str
    linux_conditions: Optional[Dict[str, Any]] = Field(alias="linuxConditions", default=None)
    windows_conditions: Optional[Dict[str, Any]] = Field(alias="windowsConditions", default=None)
    macos_conditions: Optional[Dict[str, Any]] = Field(alias="macosConditions", default=None)
    organization_ids: Optional[List[int]] = Field(alias="organizationIds", default_factory=list)
    created_at: Optional[datetime] = Field(alias="createdAt", default=None)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)
    created_by: Optional[str] = Field(alias="createdBy", default=None)
    updated_by: Optional[str] = Field(alias="updatedBy", default=None)


class CreateAutoAssetTagRequest(AIRBaseModel):
    """Create auto asset tag request model."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    tag: str
    linux_conditions: Optional[Dict[str, Any]] = Field(default=None, alias="linuxConditions")
    windows_conditions: Optional[Dict[str, Any]] = Field(default=None, alias="windowsConditions")
    macos_conditions: Optional[Dict[str, Any]] = Field(default=None, alias="macosConditions")
    organization_ids: List[int] = Field(default_factory=list, alias="organizationIds")


class UpdateAutoAssetTagRequest(AIRBaseModel):
    """Update auto asset tag request model."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    tag: Optional[str] = None
    linux_conditions: Optional[Dict[str, Any]] = Field(default=None, alias="linuxConditions")
    windows_conditions: Optional[Dict[str, Any]] = Field(default=None, alias="windowsConditions")
    macos_conditions: Optional[Dict[str, Any]] = Field(default=None, alias="macosConditions")


class StartTaggingRequest(AIRBaseModel):
    """Start tagging process request model."""
    
    filter: Dict[str, Any]
    schedulerConfig: Dict[str, Any]


class TaggingResult(AIRBaseModel):
    """Tagging process result model."""
    
    taskId: str
    message: str
    processedTags: int
    affectedAssets: int


class TaggingTask(AIRBaseModel):
    """Individual tagging task result from start tagging API."""
    
    task_id: str = Field(alias="_id")
    name: str = Field(alias="name")


class TaggingResponse(AIRBaseModel):
    """Response from start tagging API containing list of tasks."""
    
    tasks: List[TaggingTask] = []
    
    @classmethod
    def from_api_result(cls, result_list: List[Dict[str, Any]]) -> 'TaggingResponse':
        """Create TaggingResponse from API result list."""
        if not isinstance(result_list, list):
            raise ValueError("API result must be a list")
        
        tasks = [TaggingTask(**task) for task in result_list]
        return cls(tasks=tasks)
    
    @property
    def task_count(self) -> int:
        """Get the number of tasks created."""
        return len(self.tasks)
    
    def get_task_ids(self) -> List[str]:
        """Get list of all task IDs."""
        return [task.task_id for task in self.tasks]


class AutoAssetTagFilter(Filter):
    """Filter for auto asset tag queries."""
    
    tag: Optional[str] = None
    organization_ids: Optional[List[int]] = None
    search_term: Optional[str] = None
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to API parameters with proper field name mapping."""
        params = super().to_params()
        
        # Convert organization_ids to organizationIds for API compatibility
        if "filter[organization_ids]" in params:
            params["filter[organizationIds]"] = params.pop("filter[organization_ids]")
        
        # Convert search_term to searchTerm for API compatibility
        if "filter[search_term]" in params:
            params["filter[searchTerm]"] = params.pop("filter[search_term]")
            
        return params 