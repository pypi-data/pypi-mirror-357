"""
Baseline-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.baseline import (
    Baseline, BaselineProfile, BaselineComparison, BaselineSchedule, BaselineChange,
    CreateBaselineRequest, UpdateBaselineRequest, CreateBaselineProfileRequest, 
    CompareBaselineRequest
)
from ..http_client import HTTPClient


class CreateBaselineCommand(Command[Baseline]):
    """Command to create a new baseline."""
    
    def __init__(self, http_client: HTTPClient, request: CreateBaselineRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Baseline:
        """Execute the command to create a baseline."""
        data = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("baselines", json_data=data)
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "name": entity_data.get("name"),
            "description": entity_data.get("description"),
            "type": entity_data.get("type"),
            "status": entity_data.get("status", "creating"),
            "endpoint_id": entity_data.get("endpointId"),
            "endpoint_name": entity_data.get("endpointName"),
            "organization_id": entity_data.get("organizationId", 0),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
            "item_count": entity_data.get("itemCount", 0),
            "file_count": entity_data.get("fileCount", 0),
            "registry_count": entity_data.get("registryCount", 0),
            "service_count": entity_data.get("serviceCount", 0),
            "process_count": entity_data.get("processCount", 0),
            "network_connection_count": entity_data.get("networkConnectionCount", 0),
            "tags": entity_data.get("tags", []),
            "profile_id": entity_data.get("profileId"),
            "profile_name": entity_data.get("profileName"),
            "last_comparison": entity_data.get("lastComparison"),
            "comparison_count": entity_data.get("comparisonCount", 0),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return Baseline(**mapped_data)


class UpdateBaselineCommand(Command[Baseline]):
    """Command to update an existing baseline."""
    
    def __init__(self, http_client: HTTPClient, baseline_id: str, request: UpdateBaselineRequest):
        self.http_client = http_client
        self.baseline_id = baseline_id
        self.request = request
    
    def execute(self) -> Baseline:
        """Execute the command to update a baseline."""
        data = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.put(f"baselines/{self.baseline_id}", json_data=data)
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "name": entity_data.get("name"),
            "description": entity_data.get("description"),
            "type": entity_data.get("type"),
            "status": entity_data.get("status", "creating"),
            "endpoint_id": entity_data.get("endpointId"),
            "endpoint_name": entity_data.get("endpointName"),
            "organization_id": entity_data.get("organizationId", 0),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
            "item_count": entity_data.get("itemCount", 0),
            "file_count": entity_data.get("fileCount", 0),
            "registry_count": entity_data.get("registryCount", 0),
            "service_count": entity_data.get("serviceCount", 0),
            "process_count": entity_data.get("processCount", 0),
            "network_connection_count": entity_data.get("networkConnectionCount", 0),
            "tags": entity_data.get("tags", []),
            "profile_id": entity_data.get("profileId"),
            "profile_name": entity_data.get("profileName"),
            "last_comparison": entity_data.get("lastComparison"),
            "comparison_count": entity_data.get("comparisonCount", 0),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return Baseline(**mapped_data)


class DeleteBaselineCommand(Command[Dict[str, Any]]):
    """Command to delete a baseline."""
    
    def __init__(self, http_client: HTTPClient, baseline_id: str):
        self.http_client = http_client
        self.baseline_id = baseline_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to delete a baseline."""
        response = self.http_client.delete(f"baselines/{self.baseline_id}")
        return response


class CompareBaselineCommand(Command[BaselineComparison]):
    """Command to run baseline comparison."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CompareBaselineRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> BaselineComparison:
        """Execute the command to run baseline comparison."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            data = self.request
        else:
            data = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("baselines/compare", json_data=data)
        
        entity_data = response.get("result", {})
        
        # Parse changes if present
        changes = []
        for change_data in entity_data.get("changes", []):
            change_mapped = {
                "id": change_data.get("_id"),
                "comparison_id": change_data.get("comparisonId"),
                "change_type": change_data.get("changeType"),
                "item_type": change_data.get("itemType"),
                "path": change_data.get("path"),
                "old_value": change_data.get("oldValue"),
                "new_value": change_data.get("newValue"),
                "severity": change_data.get("severity", "medium"),
                "category": change_data.get("category"),
                "description": change_data.get("description"),
                "detected_at": change_data.get("detectedAt"),
                "risk_score": change_data.get("riskScore", 0.0),
            }
            
            # Remove None values
            change_mapped = {k: v for k, v in change_mapped.items() if v is not None}
            changes.append(BaselineChange(**change_mapped))
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "baseline_id": entity_data.get("baselineId"),
            "baseline_name": entity_data.get("baselineName"),
            "endpoint_id": entity_data.get("endpointId"),
            "endpoint_name": entity_data.get("endpointName"),
            "status": entity_data.get("status", "pending"),
            "started_at": entity_data.get("startedAt"),
            "completed_at": entity_data.get("completedAt"),
            "duration": entity_data.get("duration"),
            "total_changes": entity_data.get("totalChanges", 0),
            "added_items": entity_data.get("addedItems", 0),
            "removed_items": entity_data.get("removedItems", 0),
            "modified_items": entity_data.get("modifiedItems", 0),
            "moved_items": entity_data.get("movedItems", 0),
            "high_risk_changes": entity_data.get("highRiskChanges", 0),
            "medium_risk_changes": entity_data.get("mediumRiskChanges", 0),
            "low_risk_changes": entity_data.get("lowRiskChanges", 0),
            "changes": changes,
            "organization_id": entity_data.get("organizationId", 0),
            "triggered_by": entity_data.get("triggeredBy"),
            "error_message": entity_data.get("errorMessage"),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return BaselineComparison(**mapped_data)


class CreateBaselineProfileCommand(Command[BaselineProfile]):
    """Command to create a new baseline profile."""
    
    def __init__(self, http_client: HTTPClient, request: CreateBaselineProfileRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> BaselineProfile:
        """Execute the command to create a baseline profile."""
        data = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("baselines/profiles", json_data=data)
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "name": entity_data.get("name"),
            "description": entity_data.get("description"),
            "settings": entity_data.get("settings", {}),
            "categories": entity_data.get("categories", []),
            "exclusions": entity_data.get("exclusions", []),
            "organization_id": entity_data.get("organizationId", 0),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
            "is_default": entity_data.get("isDefault", False),
            "baseline_count": entity_data.get("baselineCount", 0),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return BaselineProfile(**mapped_data)


class UpdateBaselineProfileCommand(Command[BaselineProfile]):
    """Command to update an existing baseline profile."""
    
    def __init__(self, http_client: HTTPClient, profile_id: str, request: CreateBaselineProfileRequest):
        self.http_client = http_client
        self.profile_id = profile_id
        self.request = request
    
    def execute(self) -> BaselineProfile:
        """Execute the command to update a baseline profile."""
        data = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.put(f"baselines/profiles/{self.profile_id}", json_data=data)
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "name": entity_data.get("name"),
            "description": entity_data.get("description"),
            "settings": entity_data.get("settings", {}),
            "categories": entity_data.get("categories", []),
            "exclusions": entity_data.get("exclusions", []),
            "organization_id": entity_data.get("organizationId", 0),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
            "is_default": entity_data.get("isDefault", False),
            "baseline_count": entity_data.get("baselineCount", 0),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return BaselineProfile(**mapped_data)


class DeleteBaselineProfileCommand(Command[Dict[str, Any]]):
    """Command to delete a baseline profile."""
    
    def __init__(self, http_client: HTTPClient, profile_id: str):
        self.http_client = http_client
        self.profile_id = profile_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to delete a baseline profile."""
        response = self.http_client.delete(f"baselines/profiles/{self.profile_id}")
        return response


class CreateBaselineScheduleCommand(Command[BaselineSchedule]):
    """Command to create a baseline schedule."""
    
    def __init__(self, http_client: HTTPClient, baseline_id: str, schedule_data: Dict[str, Any]):
        self.http_client = http_client
        self.baseline_id = baseline_id
        self.schedule_data = schedule_data
    
    def execute(self) -> BaselineSchedule:
        """Execute the command to create a baseline schedule."""
        response = self.http_client.post("baselines/schedules", json_data=self.schedule_data)
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "baseline_id": entity_data.get("baselineId"),
            "baseline_name": entity_data.get("baselineName"),
            "schedule_type": entity_data.get("scheduleType"),
            "cron_expression": entity_data.get("cronExpression"),
            "interval_minutes": entity_data.get("intervalMinutes"),
            "enabled": entity_data.get("enabled", True),
            "next_run": entity_data.get("nextRun"),
            "last_run": entity_data.get("lastRun"),
            "run_count": entity_data.get("runCount", 0),
            "organization_id": entity_data.get("organizationId", 0),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return BaselineSchedule(**mapped_data)


class DeleteBaselineScheduleCommand(Command[Dict[str, Any]]):
    """Command to delete a baseline schedule."""
    
    def __init__(self, http_client: HTTPClient, schedule_id: str):
        self.http_client = http_client
        self.schedule_id = schedule_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to delete a baseline schedule."""
        response = self.http_client.delete(f"baselines/schedules/{self.schedule_id}")
        return response


class RefreshBaselineCommand(Command[Baseline]):
    """Command to refresh/rebuild a baseline."""
    
    def __init__(self, http_client: HTTPClient, baseline_id: str):
        self.http_client = http_client
        self.baseline_id = baseline_id
    
    def execute(self) -> Baseline:
        """Execute the command to refresh a baseline."""
        response = self.http_client.post(f"baselines/{self.baseline_id}/refresh")
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "name": entity_data.get("name"),
            "description": entity_data.get("description"),
            "type": entity_data.get("type"),
            "status": entity_data.get("status", "creating"),
            "endpoint_id": entity_data.get("endpointId"),
            "endpoint_name": entity_data.get("endpointName"),
            "organization_id": entity_data.get("organizationId", 0),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
            "item_count": entity_data.get("itemCount", 0),
            "file_count": entity_data.get("fileCount", 0),
            "registry_count": entity_data.get("registryCount", 0),
            "service_count": entity_data.get("serviceCount", 0),
            "process_count": entity_data.get("processCount", 0),
            "network_connection_count": entity_data.get("networkConnectionCount", 0),
            "tags": entity_data.get("tags", []),
            "profile_id": entity_data.get("profileId"),
            "profile_name": entity_data.get("profileName"),
            "last_comparison": entity_data.get("lastComparison"),
            "comparison_count": entity_data.get("comparisonCount", 0),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return Baseline(**mapped_data)


class AcquireBaselineByFilterCommand(Command[Dict[str, Any]]):
    """Command to acquire baselines by asset filter criteria."""
    
    def __init__(self, http_client: HTTPClient, payload: Dict[str, Any]):
        self.http_client = http_client
        self.payload = payload
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to acquire baselines by filter."""
        response = self.http_client.post("baseline/acquire", json_data=self.payload)
        return response


class CompareBaselineByEndpointCommand(Command[Dict[str, Any]]):
    """Command to compare baseline acquisition tasks by endpoint ID."""
    
    def __init__(self, http_client: HTTPClient, payload: Dict[str, Any]):
        self.http_client = http_client
        self.payload = payload
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to compare baselines by endpoint."""
        response = self.http_client.post("baseline/compare", json_data=self.payload)
        return response 