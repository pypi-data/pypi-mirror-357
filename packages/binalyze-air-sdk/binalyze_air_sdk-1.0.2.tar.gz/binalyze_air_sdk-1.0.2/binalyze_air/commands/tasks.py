"""
Task-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any

from ..base import Command
from ..http_client import HTTPClient


class CancelTaskCommand(Command[Dict[str, Any]]):
    """Command to cancel a task."""
    
    def __init__(self, http_client: HTTPClient, task_id: str):
        self.http_client = http_client
        self.task_id = task_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the cancel task command."""
        return self.http_client.post(f"tasks/{self.task_id}/cancel", json_data={})


class CancelTaskAssignmentCommand(Command[Dict[str, Any]]):
    """Command to cancel a task assignment."""
    
    def __init__(self, http_client: HTTPClient, assignment_id: str):
        self.http_client = http_client
        self.assignment_id = assignment_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the cancel task assignment command."""
        return self.http_client.post(f"tasks/assignments/{self.assignment_id}/cancel", json_data={})


class DeleteTaskAssignmentCommand(Command[Dict[str, Any]]):
    """Command to delete a task assignment."""
    
    def __init__(self, http_client: HTTPClient, assignment_id: str):
        self.http_client = http_client
        self.assignment_id = assignment_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete task assignment command."""
        return self.http_client.delete(f"tasks/assignments/{self.assignment_id}")


class DeleteTaskCommand(Command[Dict[str, Any]]):
    """Command to delete a task."""
    
    def __init__(self, http_client: HTTPClient, task_id: str):
        self.http_client = http_client
        self.task_id = task_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete task command."""
        return self.http_client.delete(f"tasks/{self.task_id}") 