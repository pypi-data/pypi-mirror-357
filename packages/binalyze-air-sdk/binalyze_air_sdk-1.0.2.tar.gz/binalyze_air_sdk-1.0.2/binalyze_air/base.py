"""
Base classes for CQRS implementation in the AIR SDK.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel as PydanticBaseModel, ConfigDict

T = TypeVar("T")


class Query(Generic[T], ABC):
    """Base class for all queries (read operations)."""
    
    @abstractmethod
    def execute(self) -> T:
        """Execute the query and return the result."""
        pass


class Command(Generic[T], ABC):
    """Base class for all commands (write operations)."""
    
    @abstractmethod
    def execute(self) -> T:
        """Execute the command and return the result."""
        pass


class AIRBaseModel(PydanticBaseModel):
    """Base Pydantic model with common configurations."""
    
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True
    )


class PaginatedResponse(AIRBaseModel, Generic[T]):
    """Generic paginated response model."""
    
    entities: List[T]
    total_entity_count: int
    current_page: int
    page_size: int
    total_page_count: int
    previous_page: Optional[int] = None
    next_page: Optional[int] = None


class APIResponse(AIRBaseModel, Generic[T]):
    """Generic API response model."""
    
    success: bool
    result: T
    status_code: int
    errors: List[str] = []


class Filter(AIRBaseModel):
    """Base filter model for queries with pagination and sorting support."""
    
    # Basic filter fields
    search_term: Optional[str] = None
    organization_ids: Optional[List[int]] = None
    
    # Pagination parameters (match API documentation exactly) - no defaults
    page_number: Optional[int] = None
    page_size: Optional[int] = None
    
    # Sorting parameters (match API documentation exactly) - no defaults
    sort_by: Optional[str] = None
    sort_type: Optional[str] = None
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to API parameters."""
        params = {}
        
        # Pagination parameters (not in filter namespace) - only if set
        if self.page_number is not None:
            params["pageNumber"] = self.page_number
        if self.page_size is not None:
            params["pageSize"] = self.page_size
        if self.sort_by is not None:
            params["sortBy"] = self.sort_by
        if self.sort_type is not None:
            params["sortType"] = self.sort_type
        
        # Filter parameters (in filter namespace)
        for field_name, field_value in self.model_dump(exclude_none=True).items():
            # Skip pagination/sorting fields as they're handled above
            if field_name in ["page_number", "page_size", "sort_by", "sort_type"]:
                continue
                
            if field_value is not None:
                if isinstance(field_value, list):
                    params[f"filter[{field_name}]"] = ",".join(map(str, field_value))
                else:
                    params[f"filter[{field_name}]"] = str(field_value)
        return params 


class PaginatedList(list):
    """List-like container that carries pagination metadata.
    This allows SDK query methods to return a normal iterable while still
    exposing additional pagination attributes such as total_entity_count.
    The class simply subclasses ``list`` and adds attributes during
    construction. All standard list operations remain intact.
    """
    def __init__(
        self,
        iterable=None,
        *,
        total_entity_count: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
        total_page_count: int | None = None,
    ) -> None:
        super().__init__(iterable or [])
        # Store metadata for caller introspection
        self.total_entity_count = total_entity_count
        self.current_page = current_page
        self.page_size = page_size
        self.total_page_count = total_page_count

    # Optional: pretty representation including meta for debugging
    def __repr__(self) -> str:  # noqa: D401
        meta = (
            f" total={self.total_entity_count} page={self.current_page} "
            f"size={self.page_size} pages={self.total_page_count}"
        )
        return f"PaginatedList({list.__repr__(self)},{meta})" 