"""
User Management API for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any

from ..http_client import HTTPClient
from ..models.user_management import (
    UserManagementUser, UserFilter, CreateUserRequest, UpdateUserRequest,
    AIUser, CreateAIUserRequest, APIUser, CreateAPIUserRequest
)
from ..queries.user_management import (
    ListUsersQuery, GetUserQuery, GetAIUserQuery, GetAPIUserQuery
)
from ..commands.user_management import (
    CreateUserCommand, UpdateUserCommand, DeleteUserCommand,
    CreateAIUserCommand, CreateAPIUserCommand
)


class UserManagementAPI:
    """User Management API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # USER QUERIES (Read operations)
    def list_users(self, filter_params: Optional[UserFilter] = None) -> List[UserManagementUser]:
        """List users with optional filtering."""
        query = ListUsersQuery(self.http_client, filter_params)
        return query.execute()
    
    def get_user(self, user_id: str) -> UserManagementUser:
        """Get a specific user by ID."""
        query = GetUserQuery(self.http_client, user_id)
        return query.execute()
    
    # USER COMMANDS (Write operations)
    def create_user(self, request: CreateUserRequest) -> UserManagementUser:
        """Create a new user."""
        command = CreateUserCommand(self.http_client, request)
        return command.execute()
    
    def update_user(self, user_id: str, request: UpdateUserRequest) -> UserManagementUser:
        """Update an existing user."""
        command = UpdateUserCommand(self.http_client, user_id, request)
        return command.execute()
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user."""
        command = DeleteUserCommand(self.http_client, user_id)
        return command.execute()
    
    # AI USER OPERATIONS
    def get_ai_user(self) -> AIUser:
        """Get the AI user."""
        query = GetAIUserQuery(self.http_client)
        return query.execute()
    
    def create_ai_user(self, request: CreateAIUserRequest) -> AIUser:
        """Create a new AI user."""
        command = CreateAIUserCommand(self.http_client, request)
        return command.execute()
    
    # API USER OPERATIONS
    def get_api_user(self) -> APIUser:
        """Get the API user."""
        query = GetAPIUserQuery(self.http_client)
        return query.execute()
    
    def create_api_user(self, request: CreateAPIUserRequest) -> APIUser:
        """Create a new API user."""
        command = CreateAPIUserCommand(self.http_client, request)
        return command.execute() 