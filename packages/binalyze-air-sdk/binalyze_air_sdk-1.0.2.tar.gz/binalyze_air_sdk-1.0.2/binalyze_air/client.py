"""
Main client for the Binalyze AIR SDK using CQRS architecture.
"""

import os
from typing import List, Optional, Union, Dict, Any
from datetime import datetime

from .config import AIRConfig
from .http_client import HTTPClient

# Import models
from .models.assets import Asset, AssetDetail, AssetTask, AssetFilter, AssetTaskFilter
from .models.cases import (
    Case, CaseActivity, CaseEndpoint, CaseTask, User, CaseFilter, CaseActivityFilter,
    CreateCaseRequest, UpdateCaseRequest, CaseNote, CaseEndpointFilter, CaseTaskFilter, CaseUserFilter
)
from .models.tasks import Task, TaskFilter, TaskAssignment
from .models.acquisitions import (
    AcquisitionProfile, AcquisitionProfileDetails, AcquisitionFilter,
    AcquisitionTaskRequest, ImageAcquisitionTaskRequest, CreateAcquisitionProfileRequest
)
from .models.policies import (
    Policy, PolicyAssignment, PolicyExecution, PolicyFilter,
    CreatePolicyRequest, UpdatePolicyRequest, AssignPolicyRequest
)
from .models.organizations import (
    Organization, OrganizationUser, OrganizationRole, OrganizationLicense,
    OrganizationSettings, OrganizationFilter, CreateOrganizationRequest,
    UpdateOrganizationRequest, AddUserToOrganizationRequest, OrganizationsPaginatedResponse,
    OrganizationUsersPaginatedResponse
)
from .models.triage import (
    TriageRule, TriageTag,
    TriageFilter, CreateTriageRuleRequest, UpdateTriageRuleRequest,
    CreateTriageTagRequest, CreateTriageProfileRequest
)
from .models.audit import (
    AuditLog, AuditSummary, AuditUserActivity, AuditSystemEvent,
    AuditRetentionPolicy, AuditFilter, AuditLogsFilter, AuditLevel
)
from .models.baseline import (
    Baseline, BaselineProfile, BaselineComparison, BaselineSchedule,
    BaselineFilter, CreateBaselineRequest, UpdateBaselineRequest,
    CreateBaselineProfileRequest, CompareBaselineRequest
)
from .models.authentication import (
    AuthStatus, LoginRequest, LoginResponse
)
from .models.user_management import (
    UserManagementUser, CreateUserRequest, UpdateUserRequest,
    AIUser, CreateAIUserRequest, APIUser, CreateAPIUserRequest, UserFilter
)
from .models.evidence import (
    EvidencePPC, EvidenceReportFileInfo, EvidenceReport
)
from .models.auto_asset_tags import (
    AutoAssetTag, CreateAutoAssetTagRequest, UpdateAutoAssetTagRequest,
    StartTaggingRequest, TaggingResult, AutoAssetTagFilter
)
from .models.evidences import (
    EvidenceRepository, AmazonS3Repository, AzureStorageRepository,
    FTPSRepository, SFTPRepository, SMBRepository, RepositoryFilter,
    CreateAmazonS3RepositoryRequest, UpdateAmazonS3RepositoryRequest,
    CreateAzureStorageRepositoryRequest, UpdateAzureStorageRepositoryRequest,
    CreateFTPSRepositoryRequest, UpdateFTPSRepositoryRequest,
    CreateSFTPRepositoryRequest, UpdateSFTPRepositoryRequest,
    CreateSMBRepositoryRequest, UpdateSMBRepositoryRequest,
    ValidateRepositoryRequest, ValidationResult
)
from .models.event_subscription import (
    EventSubscription, EventSubscriptionFilter, CreateEventSubscriptionRequest,
    UpdateEventSubscriptionRequest
)
from .models.interact import (
    ShellInteraction, AssignShellTaskRequest, ShellTaskResponse
)
from .models.params import (
    AcquisitionArtifact, EDiscoveryPattern, AcquisitionEvidence, DroneAnalyzer
)
from .models.settings import (
    BannerSettings, UpdateBannerSettingsRequest
)
from .models.endpoints import (
    EndpointTag, EndpointTagFilter
)

# Import queries
from .queries.assets import (
    ListAssetsQuery,
    GetAssetQuery,
    GetAssetTasksQuery,
)
from .queries.cases import (
    ListCasesQuery,
    GetCaseQuery,
    GetCaseActivitiesQuery,
    GetCaseEndpointsQuery,
    GetCaseTasksQuery,
    GetCaseUsersQuery,
    CheckCaseNameQuery,
)
from .queries.tasks import (
    ListTasksQuery,
    GetTaskQuery,
    GetTaskAssignmentsQuery,
)
from .queries.acquisitions import (
    ListAcquisitionProfilesQuery,
    GetAcquisitionProfileQuery,
)

# Import commands
from .commands.assets import (
    IsolateAssetsCommand,
    UnisolateAssetsCommand,
    RebootAssetsCommand,
    ShutdownAssetsCommand,
    AddTagsToAssetsCommand,
    RemoveTagsFromAssetsCommand,
    UninstallAssetsCommand,
    LogRetrievalCommand,
    VersionUpdateCommand,
)
from .commands.cases import (
    CreateCaseCommand,
    UpdateCaseCommand,
    CloseCaseCommand,
    OpenCaseCommand,
    ArchiveCaseCommand,
    ChangeCaseOwnerCommand,
    RemoveEndpointsFromCaseCommand,
    RemoveTaskAssignmentFromCaseCommand,
    ImportTaskAssignmentsToCaseCommand,
    AddNoteToCaseCommand,
    UpdateNoteToCaseCommand,
    DeleteNoteToCaseCommand,
    ExportCaseNotesCommand,
    ExportCasesCommand,
    ExportCaseEndpointsCommand,
    ExportCaseActivitiesCommand,
)
from .commands.tasks import (
    CancelTaskCommand,
    CancelTaskAssignmentCommand,
    DeleteTaskAssignmentCommand,
    DeleteTaskCommand,
)
from .commands.acquisitions import (
    CreateAcquisitionCommand,
    CreateImageAcquisitionCommand,
    CreateAcquisitionProfileCommand,
    AssignAcquisitionTaskCommand,
    AssignImageAcquisitionTaskCommand,
)

# Import API classes
from .apis.event_subscription import EventSubscriptionAPI
from .apis.interact import InteractAPI
from .apis.params import ParamsAPI
from .apis.settings import SettingsAPI
from .apis.endpoints import EndpointsAPI
from .apis.evidences import EvidencesAPI
from .apis.authentication import AuthenticationAPI
from .apis.users import UsersAPI
from .apis.evidence import EvidenceAPI
from .apis.auto_asset_tags import AutoAssetTagsAPI
from .apis.webhooks import WebhookAPI


class AssetsAPI:
    """Assets API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list(self, filter_params: Optional[AssetFilter] = None) -> List[Asset]:
        """List assets with optional filtering."""
        query = ListAssetsQuery(self.http_client, filter_params)
        return query.execute()
    
    def get(self, asset_id: str) -> AssetDetail:
        """Get a specific asset by ID."""
        query = GetAssetQuery(self.http_client, asset_id)
        return query.execute()
    
    def get_tasks(self, asset_id: str, filter_params: Optional[AssetTaskFilter] = None) -> List[AssetTask]:
        """Get tasks for a specific asset with optional filtering."""
        query = GetAssetTasksQuery(self.http_client, asset_id, filter_params)
        return query.execute()
    
    # COMMANDS (Write operations)
    def isolate(self, endpoint_ids: Union[str, List[str]], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Isolate one or more assets."""
        # Create AssetFilter from endpoint IDs for backward compatibility
        from .commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = IsolateAssetsCommand(self.http_client, asset_filter)
        return command.execute()
    
    def unisolate(self, endpoint_ids: Union[str, List[str]], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Remove isolation from one or more assets."""
        from .commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = UnisolateAssetsCommand(self.http_client, asset_filter)
        return command.execute()
    
    def reboot(self, endpoint_ids: Union[str, List[str]], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Reboot one or more assets."""
        from .commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = RebootAssetsCommand(self.http_client, asset_filter)
        return command.execute()
    
    def shutdown(self, endpoint_ids: Union[str, List[str]], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Shutdown one or more assets."""
        from .commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = ShutdownAssetsCommand(self.http_client, asset_filter)
        return command.execute()
    
    def add_tags(self, endpoint_ids: List[str], tags: List[str], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Add tags to assets."""
        from .commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = AddTagsToAssetsCommand(self.http_client, asset_filter, tags)
        return command.execute()
    
    def remove_tags(self, endpoint_ids: List[str], tags: List[str], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Remove tags from assets."""
        from .commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = RemoveTagsFromAssetsCommand(self.http_client, asset_filter, tags)
        return command.execute()
    
    def uninstall(self, endpoint_ids: List[str], purge_data: bool = False, organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Uninstall assets with optional data purging."""
        from .commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        if purge_data:
            from .commands.assets import PurgeAndUninstallAssetsCommand
            command = PurgeAndUninstallAssetsCommand(self.http_client, asset_filter)
        else:
            from .commands.assets import UninstallAssetsCommand
            command = UninstallAssetsCommand(self.http_client, asset_filter)
        return command.execute()
    
    def retrieve_logs(self, endpoint_ids: List[str], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Retrieve logs from assets."""
        from .commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = LogRetrievalCommand(self.http_client, asset_filter)
        return command.execute()
    
    def version_update(self, endpoint_ids: List[str], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Update version on assets."""
        from .commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = VersionUpdateCommand(self.http_client, asset_filter)
        return command.execute()


class CasesAPI:
    """Cases API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list(self, filter_params: Optional[CaseFilter] = None, organization_ids: Optional[List[int]] = None) -> List[Case]:
        """List cases with optional filtering."""
        query = ListCasesQuery(self.http_client, filter_params, organization_ids)
        return query.execute()
    
    def get(self, case_id: str) -> Case:
        """Get a specific case by ID."""
        query = GetCaseQuery(self.http_client, case_id)
        return query.execute()
    
    def get_activities(self, case_id: str, filter_params: Optional[CaseActivityFilter] = None) -> List[CaseActivity]:
        """Get activities for a specific case with optional filtering, pagination, and sorting."""
        query = GetCaseActivitiesQuery(self.http_client, case_id, filter_params)
        return query.execute()
    
    def get_endpoints(self, case_id: str, filter_params: Optional[CaseEndpointFilter] = None, organization_ids: Optional[List[int]] = None) -> List[CaseEndpoint]:
        """Get endpoints for a specific case with comprehensive filtering support.
        
        Args:
            case_id: The case ID to get endpoints for
            filter_params: Optional CaseEndpointFilter with comprehensive filtering options
            organization_ids: Optional list of organization IDs (for backward compatibility)
            
        Returns:
            List of CaseEndpoint objects
            
        Note: If both filter_params and organization_ids are provided, organization_ids in filter_params takes precedence.
        """
        # Handle backward compatibility
        if filter_params is None:
            filter_params = CaseEndpointFilter()
        
        # If organization_ids is provided and not set in filter_params, use it
        if organization_ids is not None and filter_params.organization_ids is None:
            filter_params.organization_ids = organization_ids
            
        query = GetCaseEndpointsQuery(self.http_client, case_id, filter_params)
        return query.execute()
    
    def get_tasks(self, case_id: str, filter_params: Optional[CaseTaskFilter] = None, organization_ids: Optional[List[int]] = None) -> List[CaseTask]:
        """Get tasks for a specific case with comprehensive filtering support.
        
        Args:
            case_id: The case ID to get tasks for
            filter_params: Optional CaseTaskFilter with comprehensive filtering options
            organization_ids: Optional list of organization IDs (for backward compatibility)
            
        Returns:
            List of CaseTask objects
            
        Note: If both filter_params and organization_ids are provided, organization_ids in filter_params takes precedence.
        """
        # Handle backward compatibility
        if filter_params is None:
            filter_params = CaseTaskFilter()
        
        # If organization_ids is provided and not set in filter_params, use it
        if organization_ids is not None and filter_params.organization_ids is None:
            filter_params.organization_ids = organization_ids
            
        query = GetCaseTasksQuery(self.http_client, case_id, filter_params)
        return query.execute()
    
    def get_users(self, case_id: str, filter_params: Optional[CaseUserFilter] = None, organization_ids: Optional[List[int]] = None) -> List[User]:
        """Get users for a specific case with comprehensive filtering support.
        
        Args:
            case_id: The case ID to get users for
            filter_params: Optional CaseUserFilter with comprehensive filtering options
            organization_ids: Optional list of organization IDs (for backward compatibility)
            
        Returns:
            List of User objects
            
        Note: If both filter_params and organization_ids are provided, organization_ids in filter_params takes precedence.
        """
        # Handle backward compatibility
        if filter_params is None:
            filter_params = CaseUserFilter()
        
        # If organization_ids is provided and not set in filter_params, use it
        if organization_ids is not None and filter_params.organization_ids is None:
            filter_params.organization_ids = organization_ids
            
        query = GetCaseUsersQuery(self.http_client, case_id, filter_params)
        return query.execute()
    
    def check_name(self, name: str) -> bool:
        """Check if a case name is available."""
        query = CheckCaseNameQuery(self.http_client, name)
        return query.execute()
    
    # COMMANDS (Write operations)
    def create(self, case_data: CreateCaseRequest) -> Case:
        """Create a new case."""
        command = CreateCaseCommand(self.http_client, case_data)
        return command.execute()
    
    def update(self, case_id: str, update_data: UpdateCaseRequest) -> Case:
        """Update an existing case."""
        command = UpdateCaseCommand(self.http_client, case_id, update_data)
        return command.execute()
    
    def close(self, case_id: str) -> Case:
        """Close a case."""
        command = CloseCaseCommand(self.http_client, case_id)
        return command.execute()
    
    def open(self, case_id: str) -> Case:
        """Open a case."""
        command = OpenCaseCommand(self.http_client, case_id)
        return command.execute()
    
    def archive(self, case_id: str) -> Case:
        """Archive a case."""
        command = ArchiveCaseCommand(self.http_client, case_id)
        return command.execute()
    
    def change_owner(self, case_id: str, new_owner_id: str) -> Case:
        """Change case owner."""
        command = ChangeCaseOwnerCommand(self.http_client, case_id, new_owner_id)
        return command.execute()
    
    def remove_endpoints(self, case_id: str, filter_params: AssetFilter) -> Dict[str, Any]:
        """Remove endpoints from a case."""
        command = RemoveEndpointsFromCaseCommand(self.http_client, case_id, filter_params)
        return command.execute()
    
    def remove_task_assignment(self, case_id: str, task_assignment_id: str) -> Dict[str, Any]:
        """Remove task assignment from a case."""
        command = RemoveTaskAssignmentFromCaseCommand(self.http_client, case_id, task_assignment_id)
        return command.execute()
    
    def import_task_assignments(self, case_id: str, task_assignment_ids: List[str]) -> Dict[str, Any]:
        """Import task assignments to a case."""
        command = ImportTaskAssignmentsToCaseCommand(self.http_client, case_id, task_assignment_ids)
        return command.execute()
    
    def add_note(self, case_id: str, note_value: str) -> CaseNote:
        """Add a note to a case."""
        command = AddNoteToCaseCommand(self.http_client, case_id, note_value)
        return command.execute()
    
    def update_note(self, case_id: str, note_id: str, note_value: str) -> CaseNote:
        """Update a note in a case."""
        command = UpdateNoteToCaseCommand(self.http_client, case_id, note_id, note_value)
        return command.execute()
    
    def delete_note(self, case_id: str, note_id: str) -> Dict[str, Any]:
        """Delete a note from a case."""
        command = DeleteNoteToCaseCommand(self.http_client, case_id, note_id)
        return command.execute()

    def export_notes(self, case_id: str) -> Dict[str, Any]:
        """Export case notes as a file download (ZIP/CSV format)."""
        command = ExportCaseNotesCommand(self.http_client, case_id)
        return command.execute()

    def export_cases(self, filter_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export cases as a CSV file download."""
        command = ExportCasesCommand(self.http_client, filter_params)
        return command.execute()

    def export_endpoints(self, case_id: str, filter_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export case endpoints as a CSV file download with optional filtering."""
        command = ExportCaseEndpointsCommand(self.http_client, case_id, filter_params)
        return command.execute()

    def export_activities(self, case_id: str, filter_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export case activities as a CSV file download with optional filtering and pagination."""
        command = ExportCaseActivitiesCommand(self.http_client, case_id, filter_params)
        return command.execute()


class TasksAPI:
    """Tasks API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list(self, filter_params: Optional[TaskFilter] = None, organization_ids: Optional[List[int]] = None) -> List[Task]:
        """List tasks with optional filtering."""
        query = ListTasksQuery(self.http_client, filter_params, organization_ids)
        return query.execute()
    
    def get(self, task_id: str) -> Task:
        """Get a specific task by ID."""
        query = GetTaskQuery(self.http_client, task_id)
        return query.execute()
    
    def get_assignments(self, task_id: str) -> List[TaskAssignment]:
        """Get task assignments for a specific task."""
        query = GetTaskAssignmentsQuery(self.http_client, task_id)
        return query.execute()
    
    # COMMANDS (Write operations)
    def cancel(self, task_id: str) -> Dict[str, Any]:
        """Cancel a task."""
        command = CancelTaskCommand(self.http_client, task_id)
        return command.execute()
    
    def cancel_assignment(self, assignment_id: str) -> Dict[str, Any]:
        """Cancel a task assignment."""
        command = CancelTaskAssignmentCommand(self.http_client, assignment_id)
        return command.execute()
    
    def delete_assignment(self, assignment_id: str) -> Dict[str, Any]:
        """Delete a task assignment."""
        command = DeleteTaskAssignmentCommand(self.http_client, assignment_id)
        return command.execute()
    
    def delete(self, task_id: str) -> Dict[str, Any]:
        """Delete a task."""
        command = DeleteTaskCommand(self.http_client, task_id)
        return command.execute()


class AcquisitionsAPI:
    """Acquisitions API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list_profiles(
        self, 
        filter_params: Optional[AcquisitionFilter] = None,
        organization_ids: Optional[List[int]] = None,
        all_organizations: bool = False
    ) -> List[AcquisitionProfile]:
        """List acquisition profiles with optional filtering."""
        query = ListAcquisitionProfilesQuery(self.http_client, filter_params, organization_ids, all_organizations)
        return query.execute()
    
    def get_profile(self, profile_id: str) -> AcquisitionProfileDetails:
        """Get a specific acquisition profile by ID."""
        query = GetAcquisitionProfileQuery(self.http_client, profile_id)
        return query.execute()
    
    # COMMANDS (Write operations)
    def acquire(self, request) -> Dict[str, Any]:
        """Assign evidence acquisition task by filter."""
        command = CreateAcquisitionCommand(self.http_client, request)
        return command.execute()
    
    def acquire_image(self, request) -> Dict[str, Any]:
        """Assign image acquisition task by filter."""
        command = CreateImageAcquisitionCommand(self.http_client, request)
        return command.execute()
    
    def create_profile(self, request: CreateAcquisitionProfileRequest) -> Dict[str, Any]:
        """Create acquisition profile."""
        command = CreateAcquisitionProfileCommand(self.http_client, request)
        return command.execute()

    # Legacy method aliases for backwards compatibility
    def assign_task(self, request: AcquisitionTaskRequest) -> List[Dict[str, Any]]:
        """Legacy alias for acquire method."""
        command = AssignAcquisitionTaskCommand(self.http_client, request)
        return command.execute()
    
    def assign_image_task(self, request: ImageAcquisitionTaskRequest) -> List[Dict[str, Any]]:
        """Legacy alias for acquire_image method."""
        command = AssignImageAcquisitionTaskCommand(self.http_client, request)
        return command.execute()


class PoliciesAPI:
    """Policies API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list(self, filter_params: Optional[PolicyFilter] = None, organization_ids: Optional[List[int]] = None) -> List[Policy]:
        """List policies with optional filtering."""
        from .queries.policies import ListPoliciesQuery
        query = ListPoliciesQuery(self.http_client, filter_params, organization_ids)
        result = query.execute()
        # Extract the policies list from the paginated response
        if hasattr(result, 'entities'):
            return result.entities
        elif isinstance(result, list):
            return result
        else:
            return []
    
    def get(self, policy_id: str) -> Policy:
        """Get a specific policy by ID."""
        from .queries.policies import GetPolicyQuery
        query = GetPolicyQuery(self.http_client, policy_id)
        return query.execute()
    
    def get_assignments(self, policy_id: str) -> List[PolicyAssignment]:
        """Get policy assignments."""
        from .queries.policies import GetPolicyAssignmentsQuery
        query = GetPolicyAssignmentsQuery(self.http_client, policy_id)
        return query.execute()
    
    def get_executions(self, policy_id: str) -> List[PolicyExecution]:
        """Get policy executions."""
        from .queries.policies import GetPolicyExecutionsQuery
        query = GetPolicyExecutionsQuery(self.http_client, policy_id)
        return query.execute()
    
    def get_match_stats(self, filter_params: Optional[Dict[str, Any]] = None, organization_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Get policy match statistics with filtering.
        
        Args:
            filter_params: Optional filter parameters (name, platform, tags, etc.)
            organization_ids: List of organization IDs (defaults to [0])
        
        Returns:
            Dictionary containing policy match statistics
        """
        try:
            # Fix API-001: Ensure organizationIds are provided to prevent errors
            if organization_ids is None or len(organization_ids) == 0:
                organization_ids = [0]  # Default to organization 0
            
            # Build payload with default filter structure
            payload = {
                "name": "",
                "searchTerm": "",
                "ipAddress": "",
                "groupId": "",
                "groupFullPath": "",
                "managedStatus": [],
                "isolationStatus": [],
                "platform": [],
                "issue": "",
                "onlineStatus": [],
                "tags": [],
                "version": "",
                "policy": "",
                "includedEndpointIds": [],
                "excludedEndpointIds": [],
                "organizationIds": organization_ids
            }
            
            # Apply custom filter parameters if provided
            if filter_params:
                for key, value in filter_params.items():
                    if key in payload:
                        payload[key] = value
            
            # Use correct API endpoint: POST policies/match-stats (not GET policies/stats)
            response = self.http_client.post("policies/match-stats", json_data=payload)
            return response
            
        except Exception as e:
            # Return a simulated response for testing
            return {
                "success": False,
                "error": str(e),
                "result": []
            }
    
    # COMMANDS (Write operations)
    def create(self, policy_data: Union[CreatePolicyRequest, Dict[str, Any]]) -> Policy:
        """Create a new policy."""
        from .commands.policies import CreatePolicyCommand
        command = CreatePolicyCommand(self.http_client, policy_data)
        return command.execute()
    
    def update(self, policy_id: str, update_data: Union[UpdatePolicyRequest, Dict[str, Any]]) -> Policy:
        """Update an existing policy."""
        from .commands.policies import UpdatePolicyCommand
        command = UpdatePolicyCommand(self.http_client, policy_id, update_data)
        return command.execute()
    
    def delete(self, policy_id: str) -> Dict[str, Any]:
        """Delete a policy."""
        from .commands.policies import DeletePolicyCommand
        command = DeletePolicyCommand(self.http_client, policy_id)
        return command.execute()
    
    def activate(self, policy_id: str) -> Policy:
        """Activate a policy."""
        from .commands.policies import ActivatePolicyCommand
        command = ActivatePolicyCommand(self.http_client, policy_id)
        return command.execute()
    
    def deactivate(self, policy_id: str) -> Policy:
        """Deactivate a policy."""
        from .commands.policies import DeactivatePolicyCommand
        command = DeactivatePolicyCommand(self.http_client, policy_id)
        return command.execute()
    
    def assign(self, assignment_data: Union[AssignPolicyRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Assign policy to endpoints."""
        from .commands.policies import AssignPolicyCommand
        command = AssignPolicyCommand(self.http_client, assignment_data)
        return command.execute()
    
    def unassign(self, policy_id: str, endpoint_ids: List[str]) -> Dict[str, Any]:
        """Unassign policy from endpoints."""
        from .commands.policies import UnassignPolicyCommand
        command = UnassignPolicyCommand(self.http_client, policy_id, endpoint_ids)
        return command.execute()
    
    def execute(self, policy_id: str, endpoint_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute a policy on assigned endpoints."""
        from .commands.policies import ExecutePolicyCommand
        command = ExecutePolicyCommand(self.http_client, policy_id, endpoint_ids)
        return command.execute()
    
    def update_priorities(self, policy_ids: List[str], organization_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Update policy priorities.
        
        Args:
            policy_ids: List of policy IDs in priority order (System policy must be first)
            organization_ids: List of organization IDs (defaults to [0])
        
        Returns:
            Response dictionary with success status
        """
        try:
            # Fix API-001: Ensure organizationIds are provided to prevent issues
            if organization_ids is None or len(organization_ids) == 0:
                organization_ids = [0]  # Default to organization 0
            
            # Use correct API parameter names according to specification
            payload = {
                "ids": policy_ids,  # API expects 'ids', not 'policyIds'
                "organizationIds": organization_ids  # Required parameter
            }
            
            response = self.http_client.put("policies/priorities", json_data=payload)
            return response
        except Exception as e:
            # Return a simulated response for testing
            return {
                "success": False,
                "error": str(e),
                "updated_policies": []
            }


class OrganizationsAPI:
    """Organizations API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list(self, page: int = 1, page_size: int = 10, 
             sort_by: str = "name", order: str = "asc") -> OrganizationsPaginatedResponse:
        """List organizations with pagination and sorting."""
        from .queries.organizations import ListOrganizationsQuery
        query = ListOrganizationsQuery(self.http_client, page, page_size, sort_by, order, None)
        return query.execute()
    
    def get(self, organization_id: str) -> Organization:
        """Get organization by ID."""
        from .queries.organizations import GetOrganizationQuery
        query = GetOrganizationQuery(self.http_client, organization_id)
        return query.execute()
    
    def get_users(self, organization_id: str, page: int = 1, page_size: int = 10) -> OrganizationUsersPaginatedResponse:
        """Get users in organization."""
        from .queries.organizations import GetOrganizationUsersQuery
        query = GetOrganizationUsersQuery(self.http_client, organization_id, page, page_size)
        return query.execute()
    
    def check_name(self, name: str) -> bool:
        """Check if organization name exists."""
        try:
            params = {"name": name}
            response = self.http_client.get("organizations/check", params=params)
            return response.get("result", False)
        except Exception:
            return False
    
    def get_shareable_deployment_info(self, deployment_token: str) -> Dict[str, Any]:
        """Get shareable deployment information by token."""
        try:
            response = self.http_client.get(f"organizations/shareable-deployment-info/{deployment_token}")
            
            if response.get("success"):
                return response.get("result", {})
            else:
                # Return error information
                return {
                    "error": True,
                    "errors": response.get("errors", []),
                    "statusCode": response.get("statusCode", 500)
                }
        except Exception as e:
            return {
                "error": True,
                "errors": [str(e)],
                "statusCode": 500
            }
    
    # COMMANDS (Write operations)
    def create(self, request: CreateOrganizationRequest) -> Organization:
        """Create organization."""
        from .commands.organizations import CreateOrganizationCommand
        command = CreateOrganizationCommand(self.http_client, request)
        return command.execute()
    
    def update(self, organization_id: str, request: UpdateOrganizationRequest) -> Organization:
        """Update organization."""
        from .commands.organizations import UpdateOrganizationCommand
        command = UpdateOrganizationCommand(self.http_client, organization_id, request)
        return command.execute()
    
    def add_user(self, organization_id: str, request: AddUserToOrganizationRequest) -> OrganizationUser:
        """Add user to organization."""
        from .commands.organizations import AddUserToOrganizationCommand
        command = AddUserToOrganizationCommand(self.http_client, organization_id, request)
        return command.execute()
    
    def assign_users(self, organization_id: str, user_ids: List[str]) -> bool:
        """Assign users to organization using the /assign-users endpoint."""
        from .commands.organizations import AssignUsersToOrganizationCommand
        from .models.organizations import AssignUsersToOrganizationRequest
        
        # Create the proper request object with correct field name
        request = AssignUsersToOrganizationRequest(userIds=user_ids)
        command = AssignUsersToOrganizationCommand(self.http_client, organization_id, request)
        return command.execute()
    
    def remove_user(self, organization_id: str, user_id: str) -> Dict[str, Any]:
        """Remove user from organization using the /remove-user endpoint."""
        from .commands.organizations import RemoveUserFromOrganizationCommand
        command = RemoveUserFromOrganizationCommand(self.http_client, organization_id, user_id)
        return command.execute()
    
    def update_settings(self, organization_id: str, settings: Dict[str, Any]) -> OrganizationSettings:
        """Update organization settings."""
        from .commands.organizations import UpdateOrganizationSettingsCommand
        command = UpdateOrganizationSettingsCommand(self.http_client, organization_id, settings)
        return command.execute()
    
    def update_shareable_deployment_settings(self, organization_id: int, status: bool) -> Dict[str, Any]:
        """Update organization shareable deployment settings."""
        try:
            # Prepare the payload according to API specification
            payload = {"status": status}
            
            # Make the API call
            response = self.http_client.post(f"organizations/{organization_id}/shareable-deployment", json_data=payload)
            return response
            
        except Exception as e:
            # Check if it's a 409 conflict (expected behavior when setting to same state)
            error_msg = str(e)
            if "409" in error_msg or "already" in error_msg.lower():
                # Return success for 409 conflicts (expected behavior)
                return {
                    "success": True,
                    "result": None,
                    "statusCode": 409,
                    "message": "Shareable deployment setting already in desired state"
                }
            
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def update_deployment_token(self, organization_id: int, deployment_token: str) -> Dict[str, Any]:
        """Update organization deployment token."""
        try:
            # Prepare the payload according to API specification
            payload = {"deploymentToken": deployment_token}
            
            # Make the API call
            response = self.http_client.post(f"organizations/{organization_id}/deployment-token", json_data=payload)
            return response
            
        except Exception as e:
            # Check if it's a 409 conflict (expected behavior when setting to same token)
            error_msg = str(e)
            if "409" in error_msg or "same token" in error_msg.lower() or "cannot be updated with same" in error_msg.lower():
                # Return success for 409 conflicts (expected behavior)
                return {
                    "success": True,
                    "result": None,
                    "statusCode": 409,
                    "message": "Deployment token already set to this value"
                }
            
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def delete(self, organization_id: int) -> Dict[str, Any]:
        """Delete organization by ID."""
        try:
            # Make the API call
            response = self.http_client.delete(f"organizations/{organization_id}")
            return response
            
        except Exception as e:
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def add_tags(self, organization_id: int, tags: List[str]) -> Dict[str, Any]:
        """Add tags to organization."""
        try:
            # Prepare the payload according to API specification
            payload = {"tags": tags}
            
            # Make the API call using PATCH method
            response = self.http_client.patch(f"organizations/{organization_id}/tags", json_data=payload)
            return response
            
        except Exception as e:
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def delete_tags(self, organization_id: int, tags: List[str]) -> Dict[str, Any]:
        """Delete tags from organization."""
        try:
            # Prepare the payload according to API specification
            payload = {"tags": tags}
            
            # Make the API call using DELETE method
            response = self.http_client.delete(f"organizations/{organization_id}/tags", json_data=payload)
            return response
            
        except Exception as e:
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def remove_tags(self, organization_id: int, tags: List[str]) -> Dict[str, Any]:
        """Remove tags from organization (alias for delete_tags)."""
        return self.delete_tags(organization_id, tags)


class TriageAPI:
    """Triage API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list_rules(self, filter_params: Optional[TriageFilter] = None, organization_ids: Optional[List[int]] = None) -> List[TriageRule]:
        """List triage rules with optional filtering."""
        from .queries.triage import ListTriageRulesQuery
        query = ListTriageRulesQuery(self.http_client, filter_params, organization_ids)
        return query.execute()
    
    def get_rule(self, rule_id: str) -> TriageRule:
        """Get a specific triage rule by ID."""
        from .queries.triage import GetTriageRuleQuery
        query = GetTriageRuleQuery(self.http_client, rule_id)
        return query.execute()
    
    def get_rule_by_id(self, rule_id: str) -> TriageRule:
        """Get a specific triage rule by ID - alias for get_rule."""
        return self.get_rule(rule_id)
    
    def list_tags(self, organization_id: Optional[int] = None) -> List[TriageTag]:
        """List triage tags."""
        from .queries.triage import ListTriageTagsQuery
        query = ListTriageTagsQuery(self.http_client, organization_id)
        return query.execute()
    
    def validate_rule(self, rule_content: str, engine: str = "yara") -> Dict[str, Any]:
        """Validate triage rule syntax."""
        try:
            # Prepare validation data
            validation_data = {
                "rule": rule_content,
                "engine": engine
            }
            
            # Call the API validation endpoint
            response = self.http_client.post("triages/rules/validate", json_data=validation_data)
            return response
            
        except Exception as e:
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    # COMMANDS (Write operations)
    def create_rule(self, request: Union[CreateTriageRuleRequest, Dict[str, Any]]) -> TriageRule:
        """Create a new triage rule."""
        from .commands.triage import CreateTriageRuleCommand
        command = CreateTriageRuleCommand(self.http_client, request)
        return command.execute()
    
    def update_rule(self, rule_id_or_data: Union[str, Dict[str, Any]], request: Optional[Union[UpdateTriageRuleRequest, Dict[str, Any]]] = None) -> TriageRule:
        """Update an existing triage rule."""
        from .commands.triage import UpdateTriageRuleCommand
        
        # Handle both signatures: update_rule(rule_id, request) and update_rule(data_dict)
        if isinstance(rule_id_or_data, str) and request is not None:
            # Traditional signature: update_rule(rule_id, request)
            command = UpdateTriageRuleCommand(self.http_client, rule_id_or_data, request)
        elif isinstance(rule_id_or_data, dict):
            # Dict signature: update_rule(data_dict) where data_dict contains 'id'
            rule_id = rule_id_or_data.get('id')
            if not rule_id:
                raise ValueError("Rule ID must be provided in data dict or as separate parameter")
            command = UpdateTriageRuleCommand(self.http_client, rule_id, rule_id_or_data)
        else:
            raise ValueError("Invalid arguments for update_rule")
        
        return command.execute()
    
    def delete_rule(self, rule_id: str) -> Dict[str, Any]:
        """Delete a triage rule."""
        from .commands.triage import DeleteTriageRuleCommand
        command = DeleteTriageRuleCommand(self.http_client, rule_id)
        return command.execute()
    
    def create_tag(self, request: Union[CreateTriageTagRequest, Dict[str, Any]]) -> TriageTag:
        """Create a new triage tag."""
        from .commands.triage import CreateTriageTagCommand
        command = CreateTriageTagCommand(self.http_client, request)
        return command.execute()
    
    def delete_tag(self, tag_id: str) -> Dict[str, Any]:
        """Delete a triage tag."""
        from .commands.triage import DeleteTriageTagCommand
        command = DeleteTriageTagCommand(self.http_client, tag_id)
        return command.execute()
    
    def assign_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a triage task to endpoints."""
        try:
            # Call the correct API endpoint for triage task assignment
            response = self.http_client.post("triages/triage", json_data=task_data)
            return response
        except Exception as e:
            # Import specific exception types
            from .exceptions import AuthorizationError, AuthenticationError, ValidationError, AIRAPIError
            
            # Handle specific API errors and preserve status codes
            if isinstance(e, (AuthorizationError, AuthenticationError, ValidationError, AIRAPIError)):
                # Return the actual API error response if available
                if hasattr(e, 'response_data') and e.response_data:
                    return e.response_data
                else:
                    # Create response matching API format with actual status code
                    return {
                        "success": False,
                        "result": None,
                        "statusCode": getattr(e, 'status_code', 500),
                        "errors": [str(e)]
                    }
            else:
                # For unexpected errors, use 500
                return {
                    "success": False,
                    "result": None,
                    "statusCode": 500,
                    "errors": [str(e)]
                }


class AuditAPI:
    """Audit logs API with enhanced filtering capabilities."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list_logs(self, filter_params: Optional[AuditLogsFilter] = None, organization_ids: Optional[int] = None) -> List[AuditLog]:
        """List audit logs with enhanced filtering - UPDATED for new POST-based API."""
        from .queries.audit import ListAuditLogsQuery
        query = ListAuditLogsQuery(self.http_client, filter_params, organization_ids)
        return query.execute()
    
    def get_log(self, log_id: str) -> AuditLog:
        """Get audit log by ID."""
        from .queries.audit import GetAuditLogQuery
        query = GetAuditLogQuery(self.http_client, log_id)
        return query.execute()
    
    def get_summary(self, organization_id: int, start_date: datetime, end_date: datetime) -> AuditSummary:
        """Get audit summary for a date range."""
        from .queries.audit import GetAuditSummaryQuery
        query = GetAuditSummaryQuery(self.http_client, organization_id, start_date, end_date)
        return query.execute()
    
    def get_user_activity(self, organization_id: int, start_date: datetime, end_date: datetime, user_id: Optional[str] = None) -> List[AuditUserActivity]:
        """Get user activity audit logs."""
        from .queries.audit import GetUserActivityQuery
        query = GetUserActivityQuery(self.http_client, organization_id, start_date, end_date, user_id)
        return query.execute()
    
    def get_system_events(self, organization_id: int, start_date: datetime, end_date: datetime, severity: Optional[AuditLevel] = None) -> List[AuditSystemEvent]:
        """Get system events audit logs."""
        from .queries.audit import GetSystemEventsQuery
        query = GetSystemEventsQuery(self.http_client, organization_id, start_date, end_date, severity)
        return query.execute()
    
    def get_retention_policy(self, organization_id: int) -> AuditRetentionPolicy:
        """Get audit retention policy."""
        from .queries.audit import GetAuditRetentionPolicyQuery
        query = GetAuditRetentionPolicyQuery(self.http_client, organization_id)
        return query.execute()
    
    def export_logs(self, filter_params: Optional[AuditLogsFilter] = None, format: str = "json", organization_ids: Optional[int] = None) -> Dict[str, Any]:
        """Export audit logs with enhanced filtering - UPDATED for new API."""
        from .queries.audit import ExportAuditLogsQuery
        query = ExportAuditLogsQuery(self.http_client, filter_params, format, organization_ids)
        return query.execute()


class BaselineAPI:
    """Baseline API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list(self, filter_params: Optional[BaselineFilter] = None, organization_ids: Optional[List[int]] = None) -> List[Baseline]:
        """List baselines with optional filtering."""
        from .queries.baseline import ListBaselinesQuery
        query = ListBaselinesQuery(self.http_client, filter_params, organization_ids)
        return query.execute()
    
    def get(self, baseline_id: str) -> Baseline:
        """Get a specific baseline by ID."""
        from .queries.baseline import GetBaselineQuery
        query = GetBaselineQuery(self.http_client, baseline_id)
        return query.execute()
    
    def get_comparisons(self, baseline_id: str) -> List[BaselineComparison]:
        """Get baseline comparisons."""
        from .queries.baseline import GetBaselineComparisonsQuery
        query = GetBaselineComparisonsQuery(self.http_client, baseline_id)
        return query.execute()
    
    def get_comparison(self, comparison_id: str) -> BaselineComparison:
        """Get a specific baseline comparison by ID."""
        from .queries.baseline import GetBaselineComparisonQuery
        query = GetBaselineComparisonQuery(self.http_client, comparison_id)
        return query.execute()
    
    def list_profiles(self, organization_ids: Optional[List[int]] = None) -> List[BaselineProfile]:
        """List baseline profiles."""
        from .queries.baseline import ListBaselineProfilesQuery
        query = ListBaselineProfilesQuery(self.http_client, organization_ids)
        return query.execute()
    
    def get_profile(self, profile_id: str) -> BaselineProfile:
        """Get a specific baseline profile by ID."""
        from .queries.baseline import GetBaselineProfileQuery
        query = GetBaselineProfileQuery(self.http_client, profile_id)
        return query.execute()
    
    def get_schedules(self, baseline_id: Optional[str] = None, organization_ids: Optional[List[int]] = None) -> List[BaselineSchedule]:
        """Get baseline schedules."""
        from .queries.baseline import GetBaselineSchedulesQuery
        query = GetBaselineSchedulesQuery(self.http_client, baseline_id, organization_ids)
        return query.execute()
    
    # COMMANDS (Write operations)
    def create(self, request: CreateBaselineRequest) -> Baseline:
        """Create a new baseline."""
        from .commands.baseline import CreateBaselineCommand
        command = CreateBaselineCommand(self.http_client, request)
        return command.execute()
    
    def update(self, baseline_id: str, request: UpdateBaselineRequest) -> Baseline:
        """Update an existing baseline."""
        from .commands.baseline import UpdateBaselineCommand
        command = UpdateBaselineCommand(self.http_client, baseline_id, request)
        return command.execute()
    
    def delete(self, baseline_id: str) -> Dict[str, Any]:
        """Delete a baseline."""
        from .commands.baseline import DeleteBaselineCommand
        command = DeleteBaselineCommand(self.http_client, baseline_id)
        return command.execute()
    
    def compare(self, request: CompareBaselineRequest) -> BaselineComparison:
        """Run a baseline comparison."""
        from .commands.baseline import CompareBaselineCommand
        command = CompareBaselineCommand(self.http_client, request)
        return command.execute()
    
    def refresh(self, baseline_id: str) -> Baseline:
        """Refresh/rebuild a baseline."""
        from .commands.baseline import RefreshBaselineCommand
        command = RefreshBaselineCommand(self.http_client, baseline_id)
        return command.execute()
    
    def create_profile(self, request: CreateBaselineProfileRequest) -> BaselineProfile:
        """Create a new baseline profile."""
        from .commands.baseline import CreateBaselineProfileCommand
        command = CreateBaselineProfileCommand(self.http_client, request)
        return command.execute()
    
    def update_profile(self, profile_id: str, request: CreateBaselineProfileRequest) -> BaselineProfile:
        """Update an existing baseline profile."""
        from .commands.baseline import UpdateBaselineProfileCommand
        command = UpdateBaselineProfileCommand(self.http_client, profile_id, request)
        return command.execute()
    
    def delete_profile(self, profile_id: str) -> Dict[str, Any]:
        """Delete a baseline profile."""
        from .commands.baseline import DeleteBaselineProfileCommand
        command = DeleteBaselineProfileCommand(self.http_client, profile_id)
        return command.execute()
    
    def create_schedule(self, baseline_id: str, schedule_data: Dict[str, Any]) -> BaselineSchedule:
        """Create a baseline schedule."""
        from .commands.baseline import CreateBaselineScheduleCommand
        command = CreateBaselineScheduleCommand(self.http_client, baseline_id, schedule_data)
        return command.execute()
    
    def delete_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Delete a baseline schedule."""
        from .commands.baseline import DeleteBaselineScheduleCommand
        command = DeleteBaselineScheduleCommand(self.http_client, schedule_id)
        return command.execute()

    def get_comparison_report(self, baseline_id: str, task_id: str) -> BaselineComparison:
        """Get comparison report - alias for get_comparison method (maintaining backward compatibility)."""
        # Use the comparison_id as the primary lookup since that's what the query expects
        return self.get_comparison(task_id)
    
    def acquire(self, baseline_data: Dict[str, Any]) -> Baseline:
        """Acquire baseline - wrapper for create method (maintaining backward compatibility)."""
        # Convert dict to CreateBaselineRequest if needed
        from .models.baseline import CreateBaselineRequest
        if isinstance(baseline_data, dict):
            request = CreateBaselineRequest(**baseline_data)
        else:
            request = baseline_data
        return self.create(request)

    def acquire_by_filter(self, filter_data: Dict[str, Any], case_id: Optional[str] = None) -> Dict[str, Any]:
        """Acquire baselines by asset filter criteria."""
        from .commands.baseline import AcquireBaselineByFilterCommand
        
        payload = {
            "filter": filter_data,
            "caseId": case_id
        }
        
        command = AcquireBaselineByFilterCommand(self.http_client, payload)
        return command.execute()

    def compare_by_endpoint(self, endpoint_id: str, baseline_task_ids: List[str]) -> Dict[str, Any]:
        """Compare baseline acquisition tasks by endpoint ID."""
        from .commands.baseline import CompareBaselineByEndpointCommand
        
        payload = {
            "endpointId": endpoint_id,
            "taskIds": baseline_task_ids
        }
        
        command = CompareBaselineByEndpointCommand(self.http_client, payload)
        return command.execute()


class AIRClient:
    """Main client for the Binalyze AIR API using CQRS architecture."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        api_token: Optional[str] = None,
        organization_id: Optional[int] = None,
        config_file: Optional[str] = None,
        config: Optional[AIRConfig] = None,
        **kwargs
    ):
        """
        Initialize the AIR client.
        
        Args:
            host: AIR instance host URL
            api_token: API token for authentication
            organization_id: Default organization ID
            config_file: Path to configuration file
            config: Pre-configured AIRConfig instance
            **kwargs: Additional configuration options
        """
        if config:
            self.config = config
        else:
            self.config = AIRConfig.create(
                host=host,
                api_token=api_token,
                organization_id=organization_id,
                config_file=config_file,
                **kwargs
            )
        
        self.http_client = HTTPClient(self.config)
        
        # Initialize API sections using CQRS pattern
        self.assets = AssetsAPI(self.http_client)
        self.cases = CasesAPI(self.http_client)
        self.tasks = TasksAPI(self.http_client)
        self.acquisitions = AcquisitionsAPI(self.http_client)
        self.policies = PoliciesAPI(self.http_client)
        self.organizations = OrganizationsAPI(self.http_client)
        self.triage = TriageAPI(self.http_client)
        self.audit = AuditAPI(self.http_client)
        self.baseline = BaselineAPI(self.http_client)
        
        # NEW API sections
        self.authentication = AuthenticationAPI(self.http_client)
        self.user_management = UsersAPI(self.http_client)
        self.evidence = EvidenceAPI(self.http_client)
        self.auto_asset_tags = AutoAssetTagsAPI(self.http_client)
        self.evidences = EvidencesAPI(self.http_client)
        
        # NEWEST API sections - 5 missing categories
        self.event_subscription = EventSubscriptionAPI(self.http_client)
        self.interact = InteractAPI(self.http_client)
        self.params = ParamsAPI(self.http_client)
        self.settings = SettingsAPI(self.http_client)
        self.endpoints = EndpointsAPI(self.http_client)
        
        # Webhook API for triggering webhook endpoints
        self.webhooks = WebhookAPI(self.http_client)
    
    def test_connection(self) -> bool:
        """Test the connection to AIR API."""
        try:
            # Try to check authentication as a simple test
            self.authentication.check_status()
            return True
        except Exception:
            return False
    
    @classmethod
    def from_environment(cls) -> "AIRClient":
        """Create client from environment variables."""
        config = AIRConfig.from_environment()
        return cls(config=config)
    
    @classmethod
    def from_config_file(cls, config_path: str = ".air_config.json") -> "AIRClient":
        """Create client from configuration file."""
        config = AIRConfig.from_file(config_path)
        return cls(config=config) 