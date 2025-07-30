"""
Interact API for the Binalyze AIR SDK.
"""

from ..http_client import HTTPClient
from ..models.interact import (
    ShellInteraction, AssignShellTaskRequest, ShellTaskResponse,  # Legacy models
    AssignInteractiveShellTaskRequest, InteractiveShellTaskResponse  # New models
)
from ..queries.interact import GetShellInteractionQuery
from ..commands.interact import AssignShellTaskCommand, AssignInteractiveShellTaskCommand


class InteractAPI:
    """Interact API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def get_shell_interaction(self, interaction_id: str) -> ShellInteraction:
        """Get a specific shell interaction by ID."""
        query = GetShellInteractionQuery(self.http_client, interaction_id)
        return query.execute()
    
    # COMMANDS (Write operations)
    def assign_interactive_shell_task(self, request: AssignInteractiveShellTaskRequest) -> InteractiveShellTaskResponse:
        """Assign an interactive shell task to an asset."""
        command = AssignInteractiveShellTaskCommand(self.http_client, request)
        return command.execute()
    
    # Legacy methods for backward compatibility (deprecated)
    def assign_shell_task(self, request: AssignShellTaskRequest) -> ShellTaskResponse:
        """Assign a shell interaction task to endpoints (legacy)."""
        command = AssignShellTaskCommand(self.http_client, request)
        return command.execute() 