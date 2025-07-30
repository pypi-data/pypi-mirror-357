"""
Task-related data models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel, Filter


class TaskStatus(str, Enum):
    """Task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Task type."""
    ACQUISITION = "acquisition"
    TRIAGE = "triage"
    ISOLATION = "isolation"
    REBOOT = "reboot"
    SHUTDOWN = "shutdown"
    IMAGE_ACQUISITION = "image-acquisition"


class NetworkCaptureConfig(AIRBaseModel):
    """Network capture configuration."""
    
    enabled: bool = False
    duration: int = 60
    pcap: Optional[Dict[str, bool]] = None
    network_flow: Optional[Dict[str, bool]] = Field(default=None, alias="networkFlow")


class PlatformEvidenceConfig(AIRBaseModel):
    """Platform-specific evidence configuration."""
    
    evidence_types: List[str] = Field(default=[], alias="evidenceTypes")
    custom: List[Any] = []
    network_capture: Optional[NetworkCaptureConfig] = Field(default=None, alias="networkCapture")


class SaveLocationConfig(AIRBaseModel):
    """Save location configuration."""
    
    location: str
    path: str
    use_most_free_volume: bool = Field(default=False, alias="useMostFreeVolume")
    volume: str = ""
    tmp: str = ""


class CompressionConfig(AIRBaseModel):
    """Compression configuration."""
    
    enabled: bool = False
    encryption: Optional[Dict[str, Any]] = None


class TaskConfig(AIRBaseModel):
    """Task configuration."""
    
    choice: Optional[str] = None
    save_to: Optional[Dict[str, SaveLocationConfig]] = Field(default=None, alias="saveTo")
    cpu: Optional[Dict[str, int]] = None
    compression: Optional[CompressionConfig] = None


class DroneConfig(AIRBaseModel):
    """Drone (analysis) configuration."""
    
    min_score: int = Field(default=0, alias="minScore")
    auto_pilot: bool = Field(default=False, alias="autoPilot")
    enabled: bool = False
    analyzers: List[str] = []
    keywords: List[str] = []


class TaskData(AIRBaseModel):
    """Task data containing configuration."""
    
    profile_id: Optional[str] = Field(default=None, alias="profileId")
    profile_name: Optional[str] = Field(default=None, alias="profileName")
    windows: Optional[PlatformEvidenceConfig] = None
    linux: Optional[PlatformEvidenceConfig] = None
    config: Optional[TaskConfig] = None
    drone: Optional[DroneConfig] = None


class TaskAssignment(AIRBaseModel):
    """Task assignment model representing a task assigned to a specific endpoint."""
    
    id: str = Field(alias="_id")
    task_id: str = Field(alias="taskId")
    name: str
    type: str
    endpoint_id: str = Field(alias="endpointId")
    endpoint_name: str = Field(alias="endpointName")
    organization_id: int = Field(default=0, alias="organizationId")
    status: str
    recurrence: Optional[str] = None
    progress: int = 0
    duration: Optional[int] = None
    durations: Optional[Dict[str, int]] = None
    case_ids: List[str] = Field(default=[], alias="caseIds")
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    created_by: Optional[str] = Field(default=None, alias="createdBy")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    response: Optional[Dict[str, Any]] = None


class Task(AIRBaseModel):
    """Task model with proper field aliases for API mapping."""
    
    id: str = Field(alias="_id")
    source: Optional[str] = None
    total_assigned_endpoints: int = Field(default=0, alias="totalAssignedEndpoints")
    total_completed_endpoints: int = Field(default=0, alias="totalCompletedEndpoints")
    total_failed_endpoints: int = Field(default=0, alias="totalFailedEndpoints")
    total_cancelled_endpoints: int = Field(default=0, alias="totalCancelledEndpoints")
    is_scheduled: bool = Field(default=False, alias="isScheduled")
    name: str
    type: str
    organization_id: int = Field(default=0, alias="organizationId")
    status: str
    created_by: str = Field(alias="createdBy")
    base_task_id: Optional[str] = Field(default=None, alias="baseTaskId")
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    recurrence: Optional[str] = None
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    data: Optional[TaskData] = None


class TaskFilter(Filter):
    """Filter for task queries."""
    
    name: Optional[str] = None
    type: Optional[List[str]] = None
    status: Optional[List[str]] = None
    created_by: Optional[str] = None
    is_scheduled: Optional[bool] = None 