"""
Evidences API for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any

from ..http_client import HTTPClient
from ..models.evidences import (
    EvidenceRepository, AmazonS3Repository, AzureStorageRepository,
    FTPSRepository, SFTPRepository, SMBRepository, RepositoryFilter,
    CreateAmazonS3RepositoryRequest, UpdateAmazonS3RepositoryRequest,
    CreateAzureStorageRepositoryRequest, UpdateAzureStorageRepositoryRequest,
    CreateFTPSRepositoryRequest, UpdateFTPSRepositoryRequest,
    CreateSFTPRepositoryRequest, UpdateSFTPRepositoryRequest,
    CreateSMBRepositoryRequest, UpdateSMBRepositoryRequest,
    ValidateRepositoryRequest, ValidationResult
)
from ..queries.evidences import (
    ListRepositoriesQuery, GetRepositoryQuery,
    ListAmazonS3RepositoriesQuery, GetAmazonS3RepositoryQuery,
    ListAzureStorageRepositoriesQuery, GetAzureStorageRepositoryQuery,
    ListFTPSRepositoriesQuery, GetFTPSRepositoryQuery,
    ListSFTPRepositoriesQuery, GetSFTPRepositoryQuery,
    ListSMBRepositoriesQuery, GetSMBRepositoryQuery
)
from ..commands.evidences import (
    UpdateRepositoryCommand, DeleteRepositoryCommand,
    CreateAmazonS3RepositoryCommand, UpdateAmazonS3RepositoryCommand, DeleteAmazonS3RepositoryCommand,
    ValidateAmazonS3RepositoryCommand,
    CreateAzureStorageRepositoryCommand, UpdateAzureStorageRepositoryCommand, DeleteAzureStorageRepositoryCommand,
    ValidateAzureStorageRepositoryCommand,
    CreateFTPSRepositoryCommand, UpdateFTPSRepositoryCommand, DeleteFTPSRepositoryCommand,
    ValidateFTPSRepositoryCommand,
    CreateSFTPRepositoryCommand, UpdateSFTPRepositoryCommand, DeleteSFTPRepositoryCommand,
    CreateSMBRepositoryCommand, UpdateSMBRepositoryCommand, DeleteSMBRepositoryCommand
)


class EvidencesAPI:
    """Evidences API with CQRS pattern - separated queries and commands for evidence repositories."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # GENERAL REPOSITORY QUERIES
    def list_repositories(self, filter_params: Optional[RepositoryFilter] = None, organization_ids: Optional[List[int]] = None) -> List[EvidenceRepository]:
        """List evidence repositories with optional filtering."""
        query = ListRepositoriesQuery(self.http_client, filter_params, organization_ids)
        return query.execute()
    
    def get_repository(self, repository_id: str) -> EvidenceRepository:
        """Get a specific evidence repository by ID."""
        query = GetRepositoryQuery(self.http_client, repository_id)
        return query.execute()
    
    def get_repository_statistics(self, repository_id: str) -> Dict[str, Any]:
        """Get statistics for a specific evidence repository."""
        # Simple statistics query - this could be enhanced based on actual API needs
        response = self.http_client.get(f"repositories/{repository_id}/statistics")
        return response.get("result", {})
    
    # GENERAL REPOSITORY COMMANDS
    def update_repository(self, repository_id: str, update_data: Dict[str, Any]) -> EvidenceRepository:
        """Update an evidence repository."""
        command = UpdateRepositoryCommand(self.http_client, repository_id, update_data)
        return command.execute()
    
    def delete_repository(self, repository_id: str) -> Dict[str, Any]:
        """Delete an evidence repository."""
        command = DeleteRepositoryCommand(self.http_client, repository_id)
        return command.execute()
    
    # AMAZON S3 REPOSITORY OPERATIONS
    def list_amazon_s3_repositories(self, filter_params: Optional[RepositoryFilter] = None) -> List[AmazonS3Repository]:
        """List Amazon S3 repositories with optional filtering."""
        query = ListAmazonS3RepositoriesQuery(self.http_client, filter_params)
        return query.execute()
    
    def get_amazon_s3_repository(self, repository_id: str) -> AmazonS3Repository:
        """Get a specific Amazon S3 repository by ID."""
        query = GetAmazonS3RepositoryQuery(self.http_client, repository_id)
        return query.execute()
    
    def create_amazon_s3_repository(self, request: CreateAmazonS3RepositoryRequest) -> AmazonS3Repository:
        """Create a new Amazon S3 repository."""
        command = CreateAmazonS3RepositoryCommand(self.http_client, request)
        return command.execute()
    
    def update_amazon_s3_repository(self, repository_id: str, request: UpdateAmazonS3RepositoryRequest) -> AmazonS3Repository:
        """Update an existing Amazon S3 repository."""
        command = UpdateAmazonS3RepositoryCommand(self.http_client, repository_id, request)
        return command.execute()
    
    def delete_amazon_s3_repository(self, repository_id: str) -> Dict[str, Any]:
        """Delete an Amazon S3 repository."""
        command = DeleteAmazonS3RepositoryCommand(self.http_client, repository_id)
        return command.execute()
    
    def validate_amazon_s3_repository(self, request: ValidateRepositoryRequest) -> ValidationResult:
        """Validate Amazon S3 repository configuration."""
        command = ValidateAmazonS3RepositoryCommand(self.http_client, request)
        return command.execute()
    
    # AZURE STORAGE REPOSITORY OPERATIONS
    def list_azure_storage_repositories(self, filter_params: Optional[RepositoryFilter] = None) -> List[AzureStorageRepository]:
        """List Azure Storage repositories with optional filtering."""
        query = ListAzureStorageRepositoriesQuery(self.http_client, filter_params)
        return query.execute()
    
    def get_azure_storage_repository(self, repository_id: str) -> AzureStorageRepository:
        """Get a specific Azure Storage repository by ID."""
        query = GetAzureStorageRepositoryQuery(self.http_client, repository_id)
        return query.execute()
    
    def create_azure_storage_repository(self, request: CreateAzureStorageRepositoryRequest) -> AzureStorageRepository:
        """Create a new Azure Storage repository."""
        command = CreateAzureStorageRepositoryCommand(self.http_client, request)
        return command.execute()
    
    def update_azure_storage_repository(self, repository_id: str, request: UpdateAzureStorageRepositoryRequest) -> AzureStorageRepository:
        """Update an existing Azure Storage repository."""
        command = UpdateAzureStorageRepositoryCommand(self.http_client, repository_id, request)
        return command.execute()
    
    def delete_azure_storage_repository(self, repository_id: str) -> Dict[str, Any]:
        """Delete an Azure Storage repository."""
        command = DeleteAzureStorageRepositoryCommand(self.http_client, repository_id)
        return command.execute()
    
    def validate_azure_storage_repository(self, request: ValidateRepositoryRequest) -> ValidationResult:
        """Validate Azure Storage repository configuration."""
        command = ValidateAzureStorageRepositoryCommand(self.http_client, request)
        return command.execute()
    
    # FTPS REPOSITORY OPERATIONS
    def list_ftps_repositories(self, filter_params: Optional[RepositoryFilter] = None) -> List[FTPSRepository]:
        """List FTPS repositories with optional filtering."""
        query = ListFTPSRepositoriesQuery(self.http_client, filter_params)
        return query.execute()
    
    def get_ftps_repository(self, repository_id: str) -> FTPSRepository:
        """Get a specific FTPS repository by ID."""
        query = GetFTPSRepositoryQuery(self.http_client, repository_id)
        return query.execute()
    
    def create_ftps_repository(self, request: CreateFTPSRepositoryRequest) -> FTPSRepository:
        """Create a new FTPS repository."""
        command = CreateFTPSRepositoryCommand(self.http_client, request)
        return command.execute()
    
    def update_ftps_repository(self, repository_id: str, request: UpdateFTPSRepositoryRequest) -> FTPSRepository:
        """Update an existing FTPS repository."""
        command = UpdateFTPSRepositoryCommand(self.http_client, repository_id, request)
        return command.execute()
    
    def delete_ftps_repository(self, repository_id: str) -> Dict[str, Any]:
        """Delete an FTPS repository."""
        command = DeleteFTPSRepositoryCommand(self.http_client, repository_id)
        return command.execute()
    
    def validate_ftps_repository(self, request: ValidateRepositoryRequest) -> ValidationResult:
        """Validate FTPS repository configuration."""
        command = ValidateFTPSRepositoryCommand(self.http_client, request)
        return command.execute()
    
    # SFTP REPOSITORY OPERATIONS
    def list_sftp_repositories(self, filter_params: Optional[RepositoryFilter] = None) -> List[SFTPRepository]:
        """List SFTP repositories with optional filtering."""
        query = ListSFTPRepositoriesQuery(self.http_client, filter_params)
        return query.execute()
    
    def get_sftp_repository(self, repository_id: str) -> SFTPRepository:
        """Get a specific SFTP repository by ID."""
        query = GetSFTPRepositoryQuery(self.http_client, repository_id)
        return query.execute()
    
    def create_sftp_repository(self, request: CreateSFTPRepositoryRequest) -> SFTPRepository:
        """Create a new SFTP repository."""
        command = CreateSFTPRepositoryCommand(self.http_client, request)
        return command.execute()
    
    def update_sftp_repository(self, repository_id: str, request: UpdateSFTPRepositoryRequest) -> SFTPRepository:
        """Update an existing SFTP repository."""
        command = UpdateSFTPRepositoryCommand(self.http_client, repository_id, request)
        return command.execute()
    
    def delete_sftp_repository(self, repository_id: str) -> Dict[str, Any]:
        """Delete an SFTP repository."""
        command = DeleteSFTPRepositoryCommand(self.http_client, repository_id)
        return command.execute()
    
    # SMB REPOSITORY OPERATIONS
    def list_smb_repositories(self, filter_params: Optional[RepositoryFilter] = None) -> List[SMBRepository]:
        """List SMB repositories with optional filtering."""
        query = ListSMBRepositoriesQuery(self.http_client, filter_params)
        return query.execute()
    
    def get_smb_repository(self, repository_id: str) -> SMBRepository:
        """Get a specific SMB repository by ID."""
        query = GetSMBRepositoryQuery(self.http_client, repository_id)
        return query.execute()
    
    def create_smb_repository(self, request: CreateSMBRepositoryRequest) -> SMBRepository:
        """Create a new SMB repository."""
        command = CreateSMBRepositoryCommand(self.http_client, request)
        return command.execute()
    
    def update_smb_repository(self, repository_id: str, request: UpdateSMBRepositoryRequest) -> SMBRepository:
        """Update an existing SMB repository."""
        command = UpdateSMBRepositoryCommand(self.http_client, repository_id, request)
        return command.execute()
    
    def delete_smb_repository(self, repository_id: str) -> Dict[str, Any]:
        """Delete an SMB repository."""
        command = DeleteSMBRepositoryCommand(self.http_client, repository_id)
        return command.execute() 