"""
Settings queries for the Binalyze AIR SDK.
"""

from ..base import Query
from ..models.settings import BannerSettings
from ..http_client import HTTPClient


class GetBannerSettingsQuery(Query[BannerSettings]):
    """Query to get banner settings."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> BannerSettings:
        """Execute the query to get banner settings."""
        response = self.http_client.get("settings/banner")
        
        return BannerSettings(**response.get("result", {})) 