"""
Interact queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.interact import ShellInteraction
from ..http_client import HTTPClient


class GetShellInteractionQuery(Query[ShellInteraction]):
    """Query to get a specific shell interaction."""
    
    def __init__(self, http_client: HTTPClient, interaction_id: str):
        self.http_client = http_client
        self.interaction_id = interaction_id
    
    def execute(self) -> ShellInteraction:
        """Execute the query to get a specific shell interaction."""
        response = self.http_client.get(f"interact/shell/{self.interaction_id}")
        
        if response.get("success"):
            result_data = response.get("result", {})
            # Use Pydantic parsing with proper field aliasing
            return ShellInteraction.model_validate(result_data)
        
        raise Exception(f"Shell interaction not found: {self.interaction_id}") 