"""
Task-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.tasks import Task, TaskFilter, TaskData, PlatformEvidenceConfig, TaskConfig, DroneConfig, TaskAssignment
from ..http_client import HTTPClient


class ListTasksQuery(Query[List[Task]]):
    """Query to list tasks with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[TaskFilter] = None, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.filter_params = filter_params or TaskFilter()
        self.organization_ids = organization_ids or [0]
    
    def execute(self) -> List[Task]:
        """Execute the query to list tasks."""
        params = self.filter_params.to_params()
        
        # Add organization IDs
        params["filter[organizationIds]"] = ",".join(map(str, self.organization_ids))
        
        # Ensure consistent sorting to match API defaults
        if "sortBy" not in params:
            params["sortBy"] = "createdAt"
        if "sortType" not in params:
            params["sortType"] = "ASC"
        
        response = self.http_client.get("tasks", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing
        tasks = []
        for entity_data in entities:
            task = Task.model_validate(entity_data)
            tasks.append(task)
        
        return tasks


class GetTaskQuery(Query[Task]):
    """Query to get a specific task by ID."""
    
    def __init__(self, http_client: HTTPClient, task_id: str):
        self.http_client = http_client
        self.task_id = task_id
    
    def execute(self) -> Task:
        """Execute the query to get a task."""
        response = self.http_client.get(f"tasks/{self.task_id}")
        
        task_data = response.get("result", {})
        
        # Use Pydantic parsing with proper field aliasing
        return Task.model_validate(task_data)


class GetTaskAssignmentsQuery(Query[List[TaskAssignment]]):
    """Query to get task assignments for a specific task."""
    
    def __init__(self, http_client: HTTPClient, task_id: str):
        self.http_client = http_client
        self.task_id = task_id
    
    def execute(self) -> List[TaskAssignment]:
        """Execute the query to get task assignments."""
        response = self.http_client.get(f"tasks/{self.task_id}/assignments")
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing
        assignments = []
        for entity_data in entities:
            assignment = TaskAssignment.model_validate(entity_data)
            assignments.append(assignment)
        
        return assignments 