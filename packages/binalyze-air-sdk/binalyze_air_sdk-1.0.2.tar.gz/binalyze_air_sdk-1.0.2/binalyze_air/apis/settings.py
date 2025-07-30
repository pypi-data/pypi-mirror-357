"""
Settings API for the Binalyze AIR SDK.
"""

from ..http_client import HTTPClient
from ..models.settings import BannerSettings, UpdateBannerSettingsRequest
from ..queries.settings import GetBannerSettingsQuery
from ..commands.settings import UpdateBannerSettingsCommand


class SettingsAPI:
    """Settings API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def get_banner_settings(self) -> BannerSettings:
        """Get current banner settings."""
        query = GetBannerSettingsQuery(self.http_client)
        return query.execute()
    
    # COMMANDS (Write operations)
    def update_banner_settings(self, request: UpdateBannerSettingsRequest) -> BannerSettings:
        """Update banner settings."""
        command = UpdateBannerSettingsCommand(self.http_client, request)
        return command.execute() 