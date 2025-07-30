"""
Authentication API for the Binalyze AIR SDK.
"""

from ..http_client import HTTPClient
from ..models.authentication import AuthStatus, LoginRequest, LoginResponse
from ..queries.authentication import CheckAuthStatusQuery
from ..commands.authentication import LoginCommand


class AuthenticationAPI:
    """Authentication API with CQRS pattern - separated queries and commands."""

    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client

    # QUERIES (Read operations)
    def check_status(self) -> AuthStatus:
        """Check current authentication status."""
        query = CheckAuthStatusQuery(self.http_client)
        return query.execute()

    # COMMANDS (Write operations)
    def login(self, request: LoginRequest) -> LoginResponse:
        """Login user with credentials."""
        command = LoginCommand(self.http_client, request)
        return command.execute()
