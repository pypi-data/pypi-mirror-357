"""
Endpoints API for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..http_client import HTTPClient
from ..models.endpoints import EndpointTag, EndpointTagFilter
from ..queries.endpoints import GetEndpointTagsQuery


class EndpointsAPI:
    """Endpoints API with CQRS pattern - read operations for endpoint management."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def get_tags(self, filter_params: Optional[EndpointTagFilter] = None) -> List[EndpointTag]:
        """Get endpoint tags with optional filtering."""
        query = GetEndpointTagsQuery(self.http_client, filter_params)
        return query.execute() 