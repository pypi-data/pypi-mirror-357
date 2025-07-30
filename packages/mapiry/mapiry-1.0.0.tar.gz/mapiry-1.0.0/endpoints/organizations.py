"""
Organization-related API endpoints for Mapiry SDK
"""

from typing import Optional, Dict, Any, List
from ..models import Organization, APIResponse
from ..utils import build_query_params


class OrganizationEndpoint:
    """
    Handles organization-related API operations.
    
    This class provides methods to manage and retrieve organization
    data from the Mapillary API.
    """
    
    def __init__(self, client):
        """
        Initialize the OrganizationEndpoint.
        
        Args:
            client: MapillaryClient instance
        """
        self.client = client
        self._filters = {}
        self._fields = []
    
    def get_by_id(self, organization_id: str, fields: Optional[List[str]] = None) -> Organization:
        """
        Get a specific organization by ID.
        
        Args:
            organization_id: Organization identifier
            fields: Fields to include in response
            
        Returns:
            Organization object
            
        Raises:
            ValueError: If organization ID is empty
        """
        if not organization_id:
            raise ValueError("Organization ID cannot be empty")
        
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        elif self._fields:
            params["fields"] = ",".join(self._fields)
        
        response_data = self.client.get(f"/{organization_id}", params=params)
        return Organization.from_dict(response_data)
    
    def get_current_user_organizations(self) -> APIResponse:
        """
        Get organizations associated with the current user.
        
        Returns:
            APIResponse containing Organization objects
        """
        endpoint = "/me/organizations"
        params = self._build_params()
        
        response_data = self.client.get(endpoint, params=params)
        return APIResponse.from_dict(response_data, Organization)
    
    def get_organization_stats(
        self, 
        organization_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for an organization.
        
        Args:
            organization_id: Organization identifier
            start_date: Start date for statistics (optional)
            end_date: End date for statistics (optional)
            
        Returns:
            Statistics dictionary
        """
        if not organization_id:
            raise ValueError("Organization ID cannot be empty")
        
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        endpoint = f"/{organization_id}/stats"
        return self.client.get(endpoint, params=params)
    
    def get_organization_images(
        self, 
        organization_id: str,
        limit: Optional[int] = None,
        fields: Optional[List[str]] = None
    ) -> APIResponse:
        """
        Get images belonging to an organization.
        
        Args:
            organization_id: Organization identifier
            limit: Maximum number of images to return
            fields: Fields to include in response
            
        Returns:
            APIResponse containing Image objects
        """
        if not organization_id:
            raise ValueError("Organization ID cannot be empty")
        
        from .images import ImageEndpoint
        from ..models import Image
        
        params = {"organization_id": organization_id}
        
        if limit:
            params["limit"] = limit
        if fields:
            params["fields"] = ",".join(fields)
        
        response_data = self.client.get("/images", params=params)
        return APIResponse.from_dict(response_data, Image)
    
    def get_organization_sequences(
        self, 
        organization_id: str,
        limit: Optional[int] = None,
        fields: Optional[List[str]] = None
    ) -> APIResponse:
        """
        Get sequences belonging to an organization.
        
        Args:
            organization_id: Organization identifier
            limit: Maximum number of sequences to return
            fields: Fields to include in response
            
        Returns:
            APIResponse containing Sequence objects
        """
        if not organization_id:
            raise ValueError("Organization ID cannot be empty")
        
        from .sequences import SequenceEndpoint
        from ..models import Sequence
        
        params = {"organization_id": organization_id}
        
        if limit:
            params["limit"] = limit
        if fields:
            params["fields"] = ",".join(fields)
        
        response_data = self.client.get("/sequences", params=params)
        return APIResponse.from_dict(response_data, Sequence)
    
    def get_organization_detections(
        self, 
        organization_id: str,
        limit: Optional[int] = None,
        fields: Optional[List[str]] = None
    ) -> APIResponse:
        """
        Get detections belonging to an organization.
        
        Args:
            organization_id: Organization identifier
            limit: Maximum number of detections to return
            fields: Fields to include in response
            
        Returns:
            APIResponse containing Detection objects
        """
        if not organization_id:
            raise ValueError("Organization ID cannot be empty")
        
        from .detections import DetectionEndpoint
        from ..models import Detection
        
        params = {"organization_id": organization_id}
        
        if limit:
            params["limit"] = limit
        if fields:
            params["fields"] = ",".join(fields)
        
        response_data = self.client.get("/map_features", params=params)
        return APIResponse.from_dict(response_data, Detection)
    
    def fields(self, *field_names: str) -> 'OrganizationEndpoint':
        """
        Specify which fields to include in the response.
        
        Args:
            *field_names: Field names to include
            
        Returns:
            OrganizationEndpoint instance for method chaining
        """
        if "all" in field_names:
            self._fields = ["all"]
        else:
            self._fields = list(field_names)
        
        return self
    
    def _build_params(self) -> Dict[str, Any]:
        """
        Build query parameters from filters.
        
        Returns:
            Dictionary of query parameters
        """
        params = self._filters.copy()
        
        if self._fields:
            params["fields"] = ",".join(self._fields)
        
        return params
    
    def _reset_filters(self):
        """Reset all filters."""
        self._filters = {}
        self._fields = []