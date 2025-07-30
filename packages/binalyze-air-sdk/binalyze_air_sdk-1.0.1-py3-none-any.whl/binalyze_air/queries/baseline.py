"""
Baseline-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.baseline import (
    Baseline, BaselineProfile, BaselineComparison, BaselineChange,
    BaselineSchedule, BaselineFilter, BaselineStatus, ComparisonStatus
)
from ..http_client import HTTPClient


class ListBaselinesQuery(Query[List[Baseline]]):
    """Query to list baselines with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[BaselineFilter] = None, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.filter_params = filter_params or BaselineFilter()
        self.organization_ids = organization_ids or [0]
    
    def execute(self) -> List[Baseline]:
        """Execute the query to list baselines."""
        params = {}
        if self.filter_params:
            params = self.filter_params.model_dump(exclude_none=True)
        
        response = self.http_client.get("baselines", params=params)
        
        if response.get("success"):
            baselines_data = response.get("result", {}).get("entities", [])
            # Use Pydantic parsing with proper field aliasing
            return [Baseline.model_validate(baseline_data) for baseline_data in baselines_data]
        
        return []


class GetBaselineQuery(Query[Baseline]):
    """Query to get a specific baseline by ID."""
    
    def __init__(self, http_client: HTTPClient, baseline_id: str):
        self.http_client = http_client
        self.baseline_id = baseline_id
    
    def execute(self) -> Baseline:
        """Execute the query to get baseline details."""
        response = self.http_client.get(f"baselines/{self.baseline_id}")
        
        if response.get("success"):
            baseline_data = response.get("result", {})
            # Use Pydantic parsing with proper field aliasing
            return Baseline.model_validate(baseline_data)
        
        raise Exception(f"Baseline not found: {self.baseline_id}")


class GetBaselineComparisonsQuery(Query[List[BaselineComparison]]):
    """Query to get baseline comparisons."""
    
    def __init__(self, http_client: HTTPClient, baseline_id: str):
        self.http_client = http_client
        self.baseline_id = baseline_id
    
    def execute(self) -> List[BaselineComparison]:
        """Execute the query to get baseline comparisons."""
        response = self.http_client.get(f"baselines/{self.baseline_id}/comparisons")
        
        if response.get("success"):
            comparisons_data = response.get("result", {}).get("entities", [])
            comparisons = []
            for comparison_data in comparisons_data:
                # Parse changes if present
                changes = []
                for change_data in comparison_data.get("changes", []):
                    # Use Pydantic parsing for changes
                    changes.append(BaselineChange.model_validate(change_data))
                
                # Add parsed changes to comparison data
                comparison_data["changes"] = changes
                
                # Use Pydantic parsing with proper field aliasing
                comparisons.append(BaselineComparison.model_validate(comparison_data))
            
            return comparisons
        
        return []


class GetBaselineComparisonQuery(Query[BaselineComparison]):
    """Query to get a specific baseline comparison by ID."""
    
    def __init__(self, http_client: HTTPClient, comparison_id: str):
        self.http_client = http_client
        self.comparison_id = comparison_id
    
    def execute(self) -> BaselineComparison:
        """Execute the query to get baseline comparison details."""
        response = self.http_client.get(f"baselines/comparisons/{self.comparison_id}")
        
        if response.get("success"):
            comparison_data = response.get("result", {})
            
            # Parse changes if present
            changes = []
            for change_data in comparison_data.get("changes", []):
                # Use Pydantic parsing for changes
                changes.append(BaselineChange.model_validate(change_data))
            
            # Add parsed changes to comparison data
            comparison_data["changes"] = changes
            
            # Use Pydantic parsing with proper field aliasing
            return BaselineComparison.model_validate(comparison_data)
        
        raise Exception(f"Baseline comparison not found: {self.comparison_id}")


class ListBaselineProfilesQuery(Query[List[BaselineProfile]]):
    """Query to list baseline profiles."""
    
    def __init__(self, http_client: HTTPClient, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.organization_ids = organization_ids or [0]
    
    def execute(self) -> List[BaselineProfile]:
        """Execute the query to list baseline profiles."""
        params = {
            "filter[organizationIds]": ",".join(map(str, self.organization_ids))
        }
        
        response = self.http_client.get("baseline-profiles", params=params)
        
        if response.get("success"):
            profiles_data = response.get("result", {}).get("entities", [])
            # Use Pydantic parsing with proper field aliasing
            return [BaselineProfile.model_validate(profile_data) for profile_data in profiles_data]
        
        return []


class GetBaselineProfileQuery(Query[BaselineProfile]):
    """Query to get a specific baseline profile by ID."""
    
    def __init__(self, http_client: HTTPClient, profile_id: str):
        self.http_client = http_client
        self.profile_id = profile_id
    
    def execute(self) -> BaselineProfile:
        """Execute the query to get baseline profile details."""
        response = self.http_client.get(f"baseline-profiles/{self.profile_id}")
        
        if response.get("success"):
            profile_data = response.get("result", {})
            # Use Pydantic parsing with proper field aliasing
            return BaselineProfile.model_validate(profile_data)
        
        raise Exception(f"Baseline profile not found: {self.profile_id}")


class GetBaselineSchedulesQuery(Query[List[BaselineSchedule]]):
    """Query to get baseline schedules."""
    
    def __init__(self, http_client: HTTPClient, baseline_id: Optional[str] = None, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.baseline_id = baseline_id
        self.organization_ids = organization_ids or [0]
    
    def execute(self) -> List[BaselineSchedule]:
        """Execute the query to get baseline schedules."""
        params = {
            "filter[organizationIds]": ",".join(map(str, self.organization_ids))
        }
        
        if self.baseline_id:
            params["baselineId"] = self.baseline_id
        
        response = self.http_client.get("baseline-schedules", params=params)
        
        if response.get("success"):
            schedules_data = response.get("result", {}).get("entities", [])
            # Use Pydantic parsing with proper field aliasing
            return [BaselineSchedule.model_validate(schedule_data) for schedule_data in schedules_data]
        
        return [] 