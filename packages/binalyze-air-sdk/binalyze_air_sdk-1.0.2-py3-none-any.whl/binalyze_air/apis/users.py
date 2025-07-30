"""
Users API for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any

from ..http_client import HTTPClient
from ..models.users import (
    User, UserFilter, CreateUserRequest, UpdateUserRequest,
    APIUser, CreateAPIUserRequest
)
from ..queries.users import (
    ListUsersQuery, GetUserQuery
)
from ..commands.users import (
    CreateUserCommand, UpdateUserCommand, DeleteUserCommand,
    CreateAPIUserCommand
)


class UsersAPI:
    """Users API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # USER QUERIES (Read operations)
    def list(self, page_number: int = 1, page_size: int = 10, 
             sort_by: str = "createdAt", sort_type: str = "ASC") -> List[User]:
        """List users with pagination support."""
        query = ListUsersQuery(self.http_client, page_number, page_size, sort_by, sort_type)
        return query.execute()
    
    def get(self, user_id: str) -> User:
        """Get a specific user by ID."""
        query = GetUserQuery(self.http_client, user_id)
        return query.execute()
    
    # USER COMMANDS (Write operations)
    def create_user(self, request: CreateUserRequest) -> User:
        """Create a new user."""
        command = CreateUserCommand(self.http_client, request)
        return command.execute()
    
    def update_user(self, user_id: str, request: UpdateUserRequest) -> User:
        """Update an existing user."""
        command = UpdateUserCommand(self.http_client, user_id, request)
        return command.execute()
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user."""
        command = DeleteUserCommand(self.http_client, user_id)
        return command.execute()
    
    # API USER OPERATIONS
    def create_api_user(self, username: str, email: str, organization_ids: List[int], 
                       profile: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a new API user for programmatic access."""
        request_data = {
            "username": username,
            "email": email,
            "organizationIds": organization_ids
        }
        if profile:
            request_data["profile"] = profile
            
        command = CreateAPIUserCommand(self.http_client, request_data)
        return command.execute() 