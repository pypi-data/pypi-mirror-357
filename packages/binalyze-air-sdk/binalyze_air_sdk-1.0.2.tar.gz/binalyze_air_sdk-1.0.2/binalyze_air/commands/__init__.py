"""
Command implementations for the Binalyze AIR SDK (CQRS pattern).
"""

from .assets import (
    IsolateAssetsCommand,
    UnisolateAssetsCommand,
    RebootAssetsCommand,
    ShutdownAssetsCommand,
    AddTagsToAssetsCommand,
    RemoveTagsFromAssetsCommand,
    UninstallAssetsCommand,
)
from .cases import (
    CreateCaseCommand,
    UpdateCaseCommand,
    CloseCaseCommand,
    OpenCaseCommand,
    ArchiveCaseCommand,
    ChangeCaseOwnerCommand,
    RemoveEndpointsFromCaseCommand,
    RemoveTaskAssignmentFromCaseCommand,
    ImportTaskAssignmentsToCaseCommand,
)
from .tasks import (
    CancelTaskCommand,
    DeleteTaskCommand,
)
from .acquisitions import (
    AssignAcquisitionTaskCommand,
    AssignImageAcquisitionTaskCommand,
    CreateAcquisitionProfileCommand,
)
from .policies import (
    CreatePolicyCommand,
    UpdatePolicyCommand,
    DeletePolicyCommand,
    ActivatePolicyCommand,
    DeactivatePolicyCommand,
    AssignPolicyCommand,
    UnassignPolicyCommand,
    ExecutePolicyCommand,
)
from .organizations import (
    CreateOrganizationCommand,
    UpdateOrganizationCommand,
    AddUserToOrganizationCommand,
    UpdateOrganizationSettingsCommand,
)
from .triage import (
    CreateTriageRuleCommand,
    UpdateTriageRuleCommand,
    DeleteTriageRuleCommand,
    EnableTriageRuleCommand,
    DisableTriageRuleCommand,
    CreateTriageTagCommand,
    DeleteTriageTagCommand,
    CreateTriageProfileCommand,
    UpdateTriageProfileCommand,
    DeleteTriageProfileCommand,
)
from .baseline import (
    CreateBaselineCommand,
    UpdateBaselineCommand,
    DeleteBaselineCommand,
    CompareBaselineCommand,
    CreateBaselineProfileCommand,
    UpdateBaselineProfileCommand,
    DeleteBaselineProfileCommand,
    CreateBaselineScheduleCommand,
    DeleteBaselineScheduleCommand,
    RefreshBaselineCommand,
)

# TODO: Add imports when implementing other endpoints  

__all__ = [
    # Asset commands
    "IsolateAssetsCommand",
    "UnisolateAssetsCommand", 
    "RebootAssetsCommand",
    "ShutdownAssetsCommand",
    "AddTagsToAssetsCommand",
    "RemoveTagsFromAssetsCommand",
    "UninstallAssetsCommand",
    
    # Case commands
    "CreateCaseCommand",
    "UpdateCaseCommand",
    "CloseCaseCommand",
    "OpenCaseCommand",
    "ArchiveCaseCommand",
    "ChangeCaseOwnerCommand",
    "RemoveEndpointsFromCaseCommand",
    "RemoveTaskAssignmentFromCaseCommand",
    "ImportTaskAssignmentsToCaseCommand",
    
    # Task commands
    "CancelTaskCommand",
    "DeleteTaskCommand",
    
    # Acquisition commands
    "AssignAcquisitionTaskCommand",
    "AssignImageAcquisitionTaskCommand",
    "CreateAcquisitionProfileCommand",
    
    # Policy commands
    "CreatePolicyCommand",
    "UpdatePolicyCommand",
    "DeletePolicyCommand",
    "ActivatePolicyCommand",
    "DeactivatePolicyCommand",
    "AssignPolicyCommand",
    "UnassignPolicyCommand",
    "ExecutePolicyCommand",
    
    # Organization commands
    "CreateOrganizationCommand",
    "UpdateOrganizationCommand",
    "AddUserToOrganizationCommand",
    "UpdateOrganizationSettingsCommand",
    
    # Triage commands
    "CreateTriageRuleCommand",
    "UpdateTriageRuleCommand",
    "DeleteTriageRuleCommand",
    "EnableTriageRuleCommand",
    "DisableTriageRuleCommand",
    "CreateTriageTagCommand",
    "DeleteTriageTagCommand",
    "CreateTriageProfileCommand",
    "UpdateTriageProfileCommand",
    "DeleteTriageProfileCommand",
    
    # Baseline commands
    "CreateBaselineCommand",
    "UpdateBaselineCommand",
    "DeleteBaselineCommand",
    "CompareBaselineCommand",
    "CreateBaselineProfileCommand",
    "UpdateBaselineProfileCommand",
    "DeleteBaselineProfileCommand",
    "CreateBaselineScheduleCommand",
    "DeleteBaselineScheduleCommand",
    "RefreshBaselineCommand",
] 