"""
Evidence API for the Binalyze AIR SDK.
"""

from typing import List, Dict, Any

from ..http_client import HTTPClient
from ..models.evidence import EvidencePPC, EvidenceReportFileInfo, EvidenceReport
from ..queries.evidence import (
    GetEvidencePPCQuery, GetEvidenceReportFileInfoQuery, GetEvidenceReportQuery
)


class EvidenceAPI:
    """Evidence API with CQRS pattern - read-only operations for case evidence."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations only - evidence is read-only)
    def get_case_evidence_ppc(self, endpoint_id: str, task_id: str) -> EvidencePPC:
        """Get case evidence PPC by endpoint ID and task ID."""
        query = GetEvidencePPCQuery(self.http_client, endpoint_id, task_id)
        return query.execute()
    
    def get_case_evidence_report_file_info(self, endpoint_id: str, task_id: str) -> EvidenceReportFileInfo:
        """Get case evidence report file info by endpoint ID and task ID."""
        query = GetEvidenceReportFileInfoQuery(self.http_client, endpoint_id, task_id)
        return query.execute()
    
    def get_case_evidence_report(self, endpoint_id: str, task_id: str) -> EvidenceReport:
        """Get case evidence report by endpoint ID and task ID."""
        query = GetEvidenceReportQuery(self.http_client, endpoint_id, task_id)
        return query.execute()
    
    # REPOSITORY OPERATIONS (Delegate to evidences API for backward compatibility)
    def list_repositories(self) -> List[Any]:
        """List evidence repositories - delegates to evidences API."""
        from .evidences import EvidencesAPI
        evidences_api = EvidencesAPI(self.http_client)
        return evidences_api.list_repositories()
    
    def get_repository(self, repository_id: str) -> Any:
        """Get repository details - delegates to evidences API."""
        from .evidences import EvidencesAPI
        evidences_api = EvidencesAPI(self.http_client)
        return evidences_api.get_repository(repository_id)
    
    def get_repository_statistics(self, repository_id: str) -> Dict[str, Any]:
        """Get repository statistics - delegates to evidences API."""
        from .evidences import EvidencesAPI
        evidences_api = EvidencesAPI(self.http_client)
        return evidences_api.get_repository_statistics(repository_id) 