"""
Endpoints queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.endpoints import EndpointTag, EndpointTagFilter
from ..http_client import HTTPClient


class GetEndpointTagsQuery(Query[List[EndpointTag]]):
    """Query to get endpoint tags."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[EndpointTagFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or EndpointTagFilter()
    
    def execute(self) -> List[EndpointTag]:
        """Execute the query to get endpoint tags."""
        params = self.filter_params.to_params()
        response = self.http_client.get("endpoints/tags", params=params)
        
        entities = response.get("result", [])
        return [EndpointTag(**item) for item in entities] 