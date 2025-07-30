"""
Interact commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.interact import (
    InteractiveShellTaskResponse, AssignInteractiveShellTaskRequest,
    ShellTaskResponse, AssignShellTaskRequest  # Legacy models
)
from ..http_client import HTTPClient


class AssignInteractiveShellTaskCommand(Command[InteractiveShellTaskResponse]):
    """Command to assign an interactive shell task."""
    
    def __init__(self, http_client: HTTPClient, request: Union[AssignInteractiveShellTaskRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> InteractiveShellTaskResponse:
        """Execute the command to assign an interactive shell task."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.post("interact/shell/assign-task", json_data=payload)
        
        if response.get("success"):
            result_data = response.get("result", {})
            # Use Pydantic parsing with proper field aliasing
            return InteractiveShellTaskResponse.model_validate(result_data)
        
        raise Exception(f"Failed to assign interactive shell task: {response.get('errors', [])}")


# Legacy command for backward compatibility (deprecated)
class AssignShellTaskCommand(Command[ShellTaskResponse]):
    """Command to assign a shell interaction task (legacy)."""
    
    def __init__(self, http_client: HTTPClient, request: Union[AssignShellTaskRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> ShellTaskResponse:
        """Execute the command to assign a shell task (legacy)."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("interact/shell/assign-task", json_data=payload)
        
        return ShellTaskResponse(**response.get("result", {})) 