"""
Users-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any

from ..base import Query
from ..models.users import User, UserFilter
from ..http_client import HTTPClient


class ListUsersQuery(Query[List[User]]):
    """Query to list users with pagination."""
    
    def __init__(self, http_client: HTTPClient, page_number: int = 1, page_size: int = 10,
                 sort_by: str = "createdAt", sort_type: str = "ASC"):
        self.http_client = http_client
        self.page_number = page_number
        self.page_size = page_size
        self.sort_by = sort_by
        self.sort_type = sort_type
    
    def execute(self) -> List[User]:
        """Execute the list users query."""
        params = {
            "pageNumber": self.page_number,
            "pageSize": self.page_size,
            "sortBy": self.sort_by,
            "sortType": self.sort_type,
            "filter[organizationIds]": "0"  # Add required filter based on API spec
        }
        
        # Use the correct endpoint path from API JSON files
        response = self.http_client.get("user-management/users", params=params)
        
        # Extract entities from response and convert to User objects
        entities = response.get("result", {}).get("entities", [])
        
        users = []
        for entity_data in entities:
            try:
                user = User.model_validate(entity_data)
                users.append(user)
            except Exception as e:
                # Log validation error but continue
                print(f"Warning: Failed to validate user data: {e}")
                continue
        
        return users


class GetUserQuery(Query[User]):
    """Query to get user by ID."""
    
    def __init__(self, http_client: HTTPClient, user_id: str):
        self.http_client = http_client
        self.user_id = user_id
    
    def execute(self) -> User:
        """Execute the get user query."""
        # Use the correct endpoint path from API JSON files
        response = self.http_client.get(f"user-management/users/{self.user_id}")
        
        # Extract user data from response and convert to User object
        entity_data = response.get("result", {})
        
        # Convert to User object using Pydantic model validation
        user = User.model_validate(entity_data)
        return user 