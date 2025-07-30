"""
Users-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.users import (
    User, CreateUserRequest, UpdateUserRequest,
    APIUser, CreateAPIUserRequest
)
from ..http_client import HTTPClient


class CreateUserCommand(Command[User]):
    """Command to create user."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateUserRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> User:
        """Execute the create user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        # Use the correct endpoint path from API JSON files
        response = self.http_client.post("user-management/users", json_data=payload)
        
        if response.get("success"):
            user_data = response.get("result", {})
            return User(**user_data)
        
        raise Exception(f"Failed to create user: {response.get('error', 'Unknown error')}")


class UpdateUserCommand(Command[User]):
    """Command to update user."""
    
    def __init__(self, http_client: HTTPClient, user_id: str, request: Union[UpdateUserRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.user_id = user_id
        self.request = request
    
    def execute(self) -> User:
        """Execute the update user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        # Use the correct endpoint path from API JSON files
        response = self.http_client.put(f"user-management/users/{self.user_id}", json_data=payload)
        
        if response.get("success"):
            user_data = response.get("result", {})
            return User(**user_data)
        
        raise Exception(f"Failed to update user: {response.get('error', 'Unknown error')}")


class DeleteUserCommand(Command[Dict[str, Any]]):
    """Command to delete user."""
    
    def __init__(self, http_client: HTTPClient, user_id: str):
        self.http_client = http_client
        self.user_id = user_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete user command."""
        # Use the correct endpoint path from API JSON files
        response = self.http_client.delete(f"user-management/users/{self.user_id}")
        
        if response.get("success"):
            return response
        
        raise Exception(f"Failed to delete user: {response.get('error', 'Unknown error')}")


class CreateAPIUserCommand(Command[Dict[str, Any]]):
    """Command to create API user."""
    
    def __init__(self, http_client: HTTPClient, request: Union[Dict[str, Any], CreateAPIUserRequest]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the create API user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        # Use the correct endpoint path from API JSON files
        response = self.http_client.post("user-management/users/api-user", json_data=payload)
        return response 