"""
Settings commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.settings import BannerSettings, UpdateBannerSettingsRequest
from ..http_client import HTTPClient


class UpdateBannerSettingsCommand(Command[BannerSettings]):
    """Command to update banner settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateBannerSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self):
        """Execute the update banner settings command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            # Use by_alias=True to ensure field aliases are properly mapped to API field names
            payload = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.put("settings/banner", json_data=payload)
        return response 