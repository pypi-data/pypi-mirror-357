"""
User Management-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.user_management import UserManagementUser, AIUser, APIUser, UserFilter
from ..http_client import HTTPClient


class ListUsersQuery(Query[List[UserManagementUser]]):
    """Query to list users."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[UserFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params
    
    def execute(self) -> List[UserManagementUser]:
        """Execute the list users query."""
        params = {}
        if self.filter_params:
            params = self.filter_params.model_dump(exclude_none=True)
        
        response = self.http_client.get("user-management/users", params=params)
        
        if response.get("success"):
            users_data = response.get("result", {}).get("entities", [])
            return [UserManagementUser(**user) for user in users_data]
        
        return []


class GetUserQuery(Query[UserManagementUser]):
    """Query to get user by ID."""
    
    def __init__(self, http_client: HTTPClient, user_id: str):
        self.http_client = http_client
        self.user_id = user_id
    
    def execute(self) -> UserManagementUser:
        """Execute the get user query."""
        response = self.http_client.get(f"user-management/users/{self.user_id}")
        
        if response.get("success"):
            user_data = response.get("result", {})
            return UserManagementUser(**user_data)
        
        raise Exception(f"User not found: {self.user_id}")


class GetAIUserQuery(Query[AIUser]):
    """Query to get AI user."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> AIUser:
        """Execute the get AI user query."""
        response = self.http_client.get("user-management/users/ai-user")
        
        if response.get("success"):
            ai_user_data = response.get("result", {})
            return AIUser(**ai_user_data)
        
        raise Exception("AI user not found")


class GetAPIUserQuery(Query[APIUser]):
    """Query to get API user."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> APIUser:
        """Execute the get API user query."""
        response = self.http_client.get("user-management/users/api-user")
        
        if response.get("success"):
            api_user_data = response.get("result", {})
            return APIUser(**api_user_data)
        
        raise Exception("API user not found") 