"""
Interact API models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel


class SendToLocation(str, Enum):
    """Send to location options."""
    USER_LOCAL = "user-local"
    REPOSITORY = "repository"
    EVIDENCE_REPOSITORY = "evidence-repository"


class TaskConfigChoice(str, Enum):
    """Task configuration choice options."""
    USE_POLICY = "use-policy"
    USE_CUSTOM_OPTIONS = "use-custom-options"


class SendToConfig(AIRBaseModel):
    """Send to configuration model."""
    
    location: SendToLocation
    repository_id: Optional[str] = Field(default=None, alias="repositoryId")
    evidence_repository_id: Optional[str] = Field(default=None, alias="evidenceRepositoryId")


class BandwidthConfig(AIRBaseModel):
    """Bandwidth configuration model."""
    
    limit: Optional[int] = None


class DiskSpaceConfig(AIRBaseModel):
    """Disk space configuration model."""
    
    reserve: Optional[int] = None


class TaskConfig(AIRBaseModel):
    """Task configuration model."""
    
    choice: TaskConfigChoice
    send_to: Optional[SendToConfig] = Field(default=None, alias="sendTo")
    bandwidth: Optional[BandwidthConfig] = None
    disk_space: Optional[DiskSpaceConfig] = Field(default=None, alias="diskSpace")


class AssignInteractiveShellTaskRequest(AIRBaseModel):
    """Request model for assigning interactive shell task."""
    
    asset_id: str = Field(alias="assetId")
    case_id: str = Field(alias="caseId")
    task_config: TaskConfig = Field(alias="taskConfig")


class InteractiveShellTaskResponse(AIRBaseModel):
    """Response model for interactive shell task assignment."""
    
    session_id: str = Field(alias="sessionId")
    idle_timeout: int = Field(alias="idleTimeout")
    config: TaskConfig


# Legacy models for backward compatibility (deprecated)
class InteractionType(str, Enum):
    """Interaction types."""
    SHELL = "shell"
    POWERSHELL = "powershell"
    CMD = "cmd"
    BASH = "bash"


class InteractionStatus(str, Enum):
    """Interaction status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ShellInteraction(AIRBaseModel):
    """Shell interaction model (legacy)."""
    
    id: str
    task_id: str
    endpoint_id: str
    endpoint_name: str
    interaction_type: InteractionType
    command: str
    output: Optional[str] = None
    error_output: Optional[str] = None
    exit_code: Optional[int] = None
    status: InteractionStatus = InteractionStatus.PENDING
    timeout: int = 300  # seconds
    organization_id: int
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None  # seconds
    environment_variables: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None


class AssignShellTaskRequest(AIRBaseModel):
    """Request model for assigning shell interaction tasks (legacy)."""
    
    endpoint_ids: List[str]
    command: str
    interaction_type: InteractionType = InteractionType.SHELL
    timeout: Optional[int] = 300
    organization_ids: Optional[List[int]] = None
    case_id: Optional[str] = None
    environment_variables: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None
    description: Optional[str] = None


class ShellTaskResponse(AIRBaseModel):
    """Response model for shell task assignment (legacy)."""
    
    task_id: str
    endpoint_interactions: List[ShellInteraction]
    success_count: int
    failure_count: int
    total_count: int
    errors: Optional[List[Dict[str, Any]]] = None 