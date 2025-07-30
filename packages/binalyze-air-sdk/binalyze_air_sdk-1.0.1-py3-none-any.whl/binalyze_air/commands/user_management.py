"""
User Management-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.user_management import (
    UserManagementUser, CreateUserRequest, UpdateUserRequest,
    AIUser, CreateAIUserRequest, APIUser, CreateAPIUserRequest
)
from ..http_client import HTTPClient


class CreateUserCommand(Command[UserManagementUser]):
    """Command to create user."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateUserRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> UserManagementUser:
        """Execute the create user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("user-management/users", json_data=payload)
        
        if response.get("success"):
            user_data = response.get("result", {})
            return UserManagementUser(**user_data)
        
        raise Exception(f"Failed to create user: {response.get('error', 'Unknown error')}")


class UpdateUserCommand(Command[UserManagementUser]):
    """Command to update user."""
    
    def __init__(self, http_client: HTTPClient, user_id: str, request: Union[UpdateUserRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.user_id = user_id
        self.request = request
    
    def execute(self) -> UserManagementUser:
        """Execute the update user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.put(f"user-management/users/{self.user_id}", json_data=payload)
        
        if response.get("success"):
            user_data = response.get("result", {})
            return UserManagementUser(**user_data)
        
        raise Exception(f"Failed to update user: {response.get('error', 'Unknown error')}")


class DeleteUserCommand(Command[Dict[str, Any]]):
    """Command to delete user."""
    
    def __init__(self, http_client: HTTPClient, user_id: str):
        self.http_client = http_client
        self.user_id = user_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete user command."""
        response = self.http_client.delete(f"user-management/users/{self.user_id}")
        
        if response.get("success"):
            return response
        
        raise Exception(f"Failed to delete user: {response.get('error', 'Unknown error')}")


class CreateAIUserCommand(Command[AIUser]):
    """Command to create AI user."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateAIUserRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> AIUser:
        """Execute the create AI user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("user-management/users/ai-user", json_data=payload)
        
        if response.get("success"):
            ai_user_data = response.get("result", {})
            return AIUser(**ai_user_data)
        
        raise Exception(f"Failed to create AI user: {response.get('error', 'Unknown error')}")


class CreateAPIUserCommand(Command[APIUser]):
    """Command to create API user."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateAPIUserRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> APIUser:
        """Execute the create API user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("user-management/users/api-user", json_data=payload)
        
        if response.get("success"):
            api_user_data = response.get("result", {})
            return APIUser(**api_user_data)
        
        raise Exception(f"Failed to create API user: {response.get('error', 'Unknown error')}") 