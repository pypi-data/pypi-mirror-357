"""
Sequence-related API endpoints for Mapiry SDK
"""

from typing import Optional, Dict, Any, List, Union, Tuple
from ..models import Sequence, APIResponse
from ..utils import (
    validate_coordinates, validate_bbox, validate_date_string,
    build_query_params
)


class SequenceEndpoint:
    """
    Handles sequence-related API operations.
    
    This class provides methods to search, filter, and retrieve sequences
    from the Mapillary API.
    """
    
    def __init__(self, client):
        """
        Initialize the SequenceEndpoint.
        
        Args:
            client: MapillaryClient instance
        """
        self.client = client
        self._filters = {}
        self._fields = []
    
    def close_to(
        self, 
        longitude: float, 
        latitude: float, 
        radius: Optional[float] = None
    ) -> 'SequenceEndpoint':
        """
        Filter sequences close to a specific point.
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            radius: Search radius in meters (optional)
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        validate_coordinates(latitude, longitude)
        
        self._filters.update({
            "longitude": longitude,
            "latitude": latitude
        })
        
        if radius is not None:
            if radius <= 0:
                raise ValueError("Radius must be positive")
            self._filters["radius"] = radius
        
        return self
    
    def in_bbox(
        self, 
        west: float, 
        south: float, 
        east: float, 
        north: float
    ) -> 'SequenceEndpoint':
        """
        Filter sequences within a bounding box.
        
        Args:
            west: Western longitude boundary
            south: Southern latitude boundary
            east: Eastern longitude boundary
            north: Northern latitude boundary
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        validate_bbox(west, south, east, north)
        
        self._filters.update({
            "bbox": f"{west},{south},{east},{north}"
        })
        
        return self
    
    def by_organization(self, organization_id: str) -> 'SequenceEndpoint':
        """
        Filter sequences by organization ID.
        
        Args:
            organization_id: Organization identifier
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        if not organization_id:
            raise ValueError("Organization ID cannot be empty")
        
        self._filters["organization_id"] = organization_id
        return self
    
    def by_creator(self, creator_id: str) -> 'SequenceEndpoint':
        """
        Filter sequences by creator ID.
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        if not creator_id:
            raise ValueError("Creator ID cannot be empty")
        
        self._filters["creator_id"] = creator_id
        return self
    
    def captured_between(
        self, 
        start_date: str, 
        end_date: Optional[str] = None
    ) -> 'SequenceEndpoint':
        """
        Filter sequences by capture date range.
        
        Args:
            start_date: Start date (YYYY, YYYY-MM, or YYYY-MM-DDTHH:MM:SS)
            end_date: End date (optional)
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        validate_date_string(start_date)
        self._filters["min_captured_at"] = start_date
        
        if end_date:
            validate_date_string(end_date)
            self._filters["max_captured_at"] = end_date
        
        return self
    
    def captured_after(self, date: str) -> 'SequenceEndpoint':
        """
        Filter sequences captured after a specific date.
        
        Args:
            date: Date string
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        return self.captured_between(date)
    
    def captured_before(self, date: str) -> 'SequenceEndpoint':
        """
        Filter sequences captured before a specific date.
        
        Args:
            date: Date string
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        validate_date_string(date)
        self._filters["max_captured_at"] = date
        return self
    
    def created_between(
        self, 
        start_date: str, 
        end_date: Optional[str] = None
    ) -> 'SequenceEndpoint':
        """
        Filter sequences by creation date range.
        
        Args:
            start_date: Start date
            end_date: End date (optional)
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        validate_date_string(start_date)
        self._filters["min_created_at"] = start_date
        
        if end_date:
            validate_date_string(end_date)
            self._filters["max_created_at"] = end_date
        
        return self
    
    def camera_make(self, make: str) -> 'SequenceEndpoint':
        """
        Filter sequences by camera make.
        
        Args:
            make: Camera manufacturer
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        if not make:
            raise ValueError("Camera make cannot be empty")
        
        self._filters["camera_make"] = make
        return self
    
    def camera_model(self, model: str) -> 'SequenceEndpoint':
        """
        Filter sequences by camera model.
        
        Args:
            model: Camera model
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        if not model:
            raise ValueError("Camera model cannot be empty")
        
        self._filters["camera_model"] = model
        return self
    
    def min_images(self, count: int) -> 'SequenceEndpoint':
        """
        Filter sequences with minimum number of images.
        
        Args:
            count: Minimum image count
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        if count <= 0:
            raise ValueError("Minimum image count must be positive")
        
        self._filters["min_image_count"] = count
        return self
    
    def fields(self, *field_names: str) -> 'SequenceEndpoint':
        """
        Specify which fields to include in the response.
        
        Args:
            *field_names: Field names to include
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        if "all" in field_names:
            self._fields = ["all"]
        else:
            self._fields = list(field_names)
        
        return self
    
    def limit(self, count: int) -> 'SequenceEndpoint':
        """
        Limit the number of results.
        
        Args:
            count: Maximum number of results
            
        Returns:
            SequenceEndpoint instance for method chaining
        """
        if count <= 0:
            raise ValueError("Limit must be positive")
        
        self._filters["limit"] = count
        return self
    
    def get(self) -> APIResponse:
        """
        Execute the query and return results.
        
        Returns:
            APIResponse containing Sequence objects
        """
        endpoint = "/sequences"
        params = self._build_params()
        
        response_data = self.client.get(endpoint, params=params)
        return APIResponse.from_dict(response_data, Sequence)
    
    def get_by_id(self, sequence_id: str, fields: Optional[List[str]] = None) -> Sequence:
        """
        Get a specific sequence by ID.
        
        Args:
            sequence_id: Sequence identifier
            fields: Fields to include in response
            
        Returns:
            Sequence object
        """
        if not sequence_id:
            raise ValueError("Sequence ID cannot be empty")
        
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        elif self._fields:
            params["fields"] = ",".join(self._fields)
        
        response_data = self.client.get(f"/{sequence_id}", params=params)
        return Sequence.from_dict(response_data)
    
    def get_images(
        self, 
        sequence_id: str, 
        fields: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> APIResponse:
        """
        Get images belonging to a specific sequence.
        
        Args:
            sequence_id: Sequence identifier
            fields: Fields to include in response
            limit: Maximum number of images to return
            
        Returns:
            APIResponse containing Image objects
        """
        if not sequence_id:
            raise ValueError("Sequence ID cannot be empty")
        
        from .images import ImageEndpoint
        from ..models import Image
        
        params = {"sequence_id": sequence_id}
        
        if fields:
            params["fields"] = ",".join(fields)
        if limit:
            params["limit"] = limit
        
        response_data = self.client.get("/images", params=params)
        return APIResponse.from_dict(response_data, Image)
    
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