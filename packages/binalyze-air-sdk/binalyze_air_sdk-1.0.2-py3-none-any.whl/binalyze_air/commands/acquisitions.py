"""
Acquisition-related commands for the Binalyze AIR SDK.
Fixed to match API documentation exactly.
"""

from typing import List, Dict, Any

from ..base import Command
from ..models.acquisitions import (
    AcquisitionTaskRequest, ImageAcquisitionTaskRequest, CreateAcquisitionProfileRequest,
    CreateAcquisitionRequest, CreateImageAcquisitionRequest
)
from ..models.assets import AssetFilter
from ..http_client import HTTPClient


class AssignAcquisitionTaskCommand(Command[List[Dict[str, Any]]]):
    """Command to assign acquisition task - FIXED to match API documentation exactly."""
    
    def __init__(self, http_client: HTTPClient, request: AcquisitionTaskRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> List[Dict[str, Any]]:
        """Execute the acquisition task assignment with correct payload structure."""
        # FIXED: Use proper API payload structure as per documentation
        payload = {
            "caseId": self.request.case_id,
            "acquisitionProfileId": self.request.acquisition_profile_id,
            "droneConfig": {
                "autoPilot": self.request.drone_config.auto_pilot if self.request.drone_config else False,
                "enabled": self.request.drone_config.enabled if self.request.drone_config else False,
                "analyzers": self.request.drone_config.analyzers if self.request.drone_config else ["bha", "wsa", "aa", "ara"],
                "keywords": self.request.drone_config.keywords if self.request.drone_config else []
            },
            "taskConfig": {
                "choice": self.request.task_config.choice if self.request.task_config else "use-custom-options",
                "saveTo": {
                    "windows": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "repositoryId": None,
                        "path": "Binalyze\\AIR\\",
                        "volume": "C:",
                        "tmp": "Binalyze\\AIR\\tmp",
                        "directCollection": False
                    },
                    "linux": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "repositoryId": None,
                        "path": "opt/binalyze/air",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "macos": {
                        "location": "local",
                        "useMostFreeVolume": False,
                        "repositoryId": None,
                        "path": "opt/binalyze/air",
                        "volume": "/",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "aix": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "path": "opt/binalyze/air",
                        "volume": "/",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    }
                },
                "cpu": self.request.task_config.cpu if self.request.task_config else {"limit": 80},
                "compression": self.request.task_config.compression if self.request.task_config else {
                    "enabled": True,
                    "encryption": {
                        "enabled": False,
                        "password": ""
                    }
                }
            },
            "filter": {
                "searchTerm": self.request.filter.search_term or "",
                "name": self.request.filter.name or "",
                "ipAddress": self.request.filter.ip_address or "",
                "groupId": self.request.filter.group_id or "",
                "groupFullPath": self.request.filter.group_full_path or "",
                "managedStatus": self.request.filter.managed_status or [],
                "isolationStatus": self.request.filter.isolation_status or [],
                "platform": self.request.filter.platform or [],
                "issue": self.request.filter.issue or "",
                "onlineStatus": self.request.filter.online_status or [],
                "tags": self.request.filter.tags or [],
                "version": self.request.filter.version or "",
                "policy": self.request.filter.policy or "",
                "includedEndpointIds": self.request.filter.included_endpoint_ids or [],
                "excludedEndpointIds": self.request.filter.excluded_endpoint_ids or [],
                "organizationIds": self.request.filter.organization_ids or [0]
            },
            "schedulerConfig": {
                "when": "now"
            }
        }
        
        # FIXED: Correct endpoint URL
        response = self.http_client.post("acquisitions/acquire", json_data=payload)
        
        return response.get("result", [])


class CreateAcquisitionCommand(Command[Dict[str, Any]]):
    """Command to create acquisition task using simplified request - FIXED to match API."""
    
    def __init__(self, http_client: HTTPClient, request: CreateAcquisitionRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the acquisition task assignment with correct structure."""
        # FIXED: Use proper filter structure instead of direct filter object
        payload = {
            "caseId": getattr(self.request, 'case_id', None),
            "acquisitionProfileId": self.request.profileId,
            "droneConfig": {
                "autoPilot": False,
                "enabled": False,
                "analyzers": ["bha", "wsa", "aa", "ara"],
                "keywords": []
            },
            "taskConfig": {
                "choice": "use-custom-options",
                "saveTo": {
                    "windows": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "repositoryId": None,
                        "path": "Binalyze\\AIR\\",
                        "volume": "C:",
                        "tmp": "Binalyze\\AIR\\tmp",
                        "directCollection": False
                    },
                    "linux": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "repositoryId": None,
                        "path": "opt/binalyze/air",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "macos": {
                        "location": "local",
                        "useMostFreeVolume": False,
                        "repositoryId": None,
                        "path": "opt/binalyze/air",
                        "volume": "/",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "aix": {
                        "location": "local",
                        "useMostFreeVolume": True,
                        "path": "opt/binalyze/air",
                        "volume": "/",
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    }
                },
                "cpu": {
                    "limit": 80
                },
                "compression": {
                    "enabled": True,
                    "encryption": {
                        "enabled": False,
                        "password": ""
                    }
                }
            },
            "filter": self.request.filter.to_filter_dict() if isinstance(self.request.filter, AssetFilter) else self.request.filter,
            "schedulerConfig": {
                "when": "now"
            }
        }
        
        if hasattr(self.request, 'name') and self.request.name:
            payload["taskName"] = self.request.name
        
        return self.http_client.post("acquisitions/acquire", json_data=payload)


class AssignImageAcquisitionTaskCommand(Command[List[Dict[str, Any]]]):
    """Command to assign image acquisition task - FIXED endpoint URL."""
    
    def __init__(self, http_client: HTTPClient, request: ImageAcquisitionTaskRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> List[Dict[str, Any]]:
        """Execute the image acquisition task assignment."""
        # Convert request to API payload using correct model attributes
        payload = {
            "caseId": self.request.case_id,
            "endpoints": [
                {
                    "endpointId": endpoint.endpoint_id,
                    "volumes": endpoint.volumes
                }
                for endpoint in self.request.disk_image_options.endpoints
            ],
            "organizationIds": self.request.filter.organization_ids,
            "startOffset": self.request.disk_image_options.start_offset,
            "chunkSize": self.request.disk_image_options.chunk_size,
            "chunkCount": self.request.disk_image_options.chunk_count,
            "enableCompression": self.request.task_config.compression.get("enabled", False) if self.request.task_config else False,
            "enableEncryption": self.request.task_config.compression.get("encryption", {}).get("enabled", False) if self.request.task_config else False,
        }
        
        if self.request.task_config and self.request.task_config.compression.get("encryption", {}).get("password"):
            payload["encryptionPassword"] = self.request.task_config.compression["encryption"]["password"]
        
        # FIXED: Correct endpoint URL
        response = self.http_client.post("acquisitions/acquire/image", json_data=payload)
        
        return response.get("result", [])


class CreateImageAcquisitionCommand(Command[Dict[str, Any]]):
    """Command to create image acquisition task using simplified request - FIXED structure."""
    
    def __init__(self, http_client: HTTPClient, request: CreateImageAcquisitionRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the image acquisition task assignment with correct structure."""
        # Extract repository ID from request if available (for now use a placeholder)
        # This should be enhanced to get actual repository ID dynamically
        repository_id = getattr(self.request, 'repository_id', None)
        
        # Build the complete payload structure that matches the API specification
        payload = {
            "caseId": getattr(self.request, 'case_id', None),
            "taskConfig": {
                "choice": "use-custom-options",
                "saveTo": {
                    "windows": {
                        "location": "repository",
                        "path": "Binalyze\\AIR\\",
                        "useMostFreeVolume": True,
                        "repositoryId": repository_id,
                        "tmp": "Binalyze\\AIR\\tmp",
                        "directCollection": False
                    },
                    "linux": {
                        "location": "repository",
                        "path": "opt/binalyze/air",
                        "useMostFreeVolume": False,
                        "repositoryId": repository_id,
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    },
                    "macos": {
                        "location": "repository",
                        "path": "opt/binalyze/air",
                        "useMostFreeVolume": False,
                        "repositoryId": repository_id,
                        "tmp": "opt/binalyze/air/tmp",
                        "directCollection": False
                    }
                },
                "bandwidth": {
                    "limit": 100000
                },
                "compression": {
                    "enabled": True,
                    "encryption": {
                        "enabled": False,
                        "password": ""
                    }
                }
            },
            "diskImageOptions": {
                "imageType": "dd",
                "chunkSize": 1048576,
                "chunkCount": 0,
                "startOffset": 0,
                "singleFile": False,
                "endpoints": [
                    {
                        "endpointId": "placeholder",  # Will be replaced with actual endpoint IDs
                        "volumes": ["/"]  # Default volumes, should be replaced with actual volumes
                    }
                ]
            },
            "filter": self.request.filter.to_filter_dict() if isinstance(self.request.filter, AssetFilter) else self.request.filter,
            "schedulerConfig": {
                "when": "now"
            }
        }
        
        # Extract endpoint IDs from filter and use them in diskImageOptions
        if isinstance(self.request.filter, dict):
            included_endpoints = self.request.filter.get('includedEndpointIds', [])
        else:
            included_endpoints = getattr(self.request.filter, 'included_endpoint_ids', [])
        
        # Get volumes from request or use defaults
        volumes = getattr(self.request, 'volumes', None) or ["/", "C:"]
        
        if included_endpoints:
            payload["diskImageOptions"]["endpoints"] = [
                {
                    "endpointId": endpoint_id,
                    "volumes": volumes  # Use actual discovered volumes
                }
                for endpoint_id in included_endpoints
            ]
        
        if hasattr(self.request, 'name') and self.request.name:
            payload["taskName"] = self.request.name
        
        return self.http_client.post("acquisitions/acquire/image", json_data=payload)


class CreateAcquisitionProfileCommand(Command[Dict[str, Any]]):
    """Command to create acquisition profile - FIXED endpoint URL."""
    
    def __init__(self, http_client: HTTPClient, request: CreateAcquisitionProfileRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the create acquisition profile command."""
        # Build the payload
        payload = {
            "name": self.request.name,
            "organizationIds": self.request.organization_ids
        }
        
        # Convert platform configuration to API format (snake_case -> camelCase)
        def convert_platform_to_api(platform_data):
            if not platform_data:
                return None
            
            api_data = {}
            if platform_data.get("evidence_list"):
                api_data["evidenceList"] = platform_data["evidence_list"]
            if platform_data.get("artifact_list"):
                api_data["artifactList"] = platform_data["artifact_list"]
            if platform_data.get("custom_content_profiles") is not None:
                api_data["customContentProfiles"] = platform_data["custom_content_profiles"]
            
            # Convert network capture configuration
            if platform_data.get("network_capture"):
                nc = platform_data["network_capture"]
                api_data["networkCapture"] = {
                    "enabled": nc.get("enabled", False),
                    "duration": nc.get("duration", 600),
                    "pcap": nc.get("pcap", {"enabled": False}),
                    "networkFlow": nc.get("network_flow", {"enabled": False})
                }
            
            return api_data
        
        # Only add platform configurations if they have content
        if self.request.windows:
            payload["windows"] = convert_platform_to_api(self.request.windows.model_dump())
        if self.request.linux:
            payload["linux"] = convert_platform_to_api(self.request.linux.model_dump())
        if self.request.macos:
            payload["macos"] = convert_platform_to_api(self.request.macos.model_dump())
        if self.request.aix:
            payload["aix"] = convert_platform_to_api(self.request.aix.model_dump())
        
        # Only add eDiscovery if it has content
        if self.request.e_discovery:
            payload["eDiscovery"] = self.request.e_discovery
        
        if self.request.description:
            payload["description"] = self.request.description
            
        if self.request.artifacts:
            payload["artifacts"] = self.request.artifacts
        
        # FIXED: Correct endpoint URL
        return self.http_client.post("acquisitions/profiles", json_data=payload) 