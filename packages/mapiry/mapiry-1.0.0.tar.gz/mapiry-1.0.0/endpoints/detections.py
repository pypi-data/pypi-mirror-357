"""
Detection-related API endpoints for Mapiry SDK
"""

from typing import Optional, Dict, Any, List, Union
from ..models import Detection, APIResponse
from ..utils import (
    validate_coordinates, validate_bbox, validate_date_string,
    build_query_params
)


class DetectionEndpoint:
    """
    Handles detection-related API operations.
    
    This class provides methods to search, filter, and retrieve object
    detections from the Mapillary API.
    """
    
    def __init__(self, client):
        """
        Initialize the DetectionEndpoint.
        
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
    ) -> 'DetectionEndpoint':
        """
        Filter detections close to a specific point.
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            radius: Search radius in meters (optional)
            
        Returns:
            DetectionEndpoint instance for method chaining
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
    ) -> 'DetectionEndpoint':
        """
        Filter detections within a bounding box.
        
        Args:
            west: Western longitude boundary
            south: Southern latitude boundary
            east: Eastern longitude boundary
            north: Northern latitude boundary
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        validate_bbox(west, south, east, north)
        
        self._filters.update({
            "bbox": f"{west},{south},{east},{north}"
        })
        
        return self
    
    def by_image(self, image_id: str) -> 'DetectionEndpoint':
        """
        Filter detections by image ID.
        
        Args:
            image_id: Image identifier
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        if not image_id:
            raise ValueError("Image ID cannot be empty")
        
        self._filters["image_id"] = image_id
        return self
    
    def by_sequence(self, sequence_id: str) -> 'DetectionEndpoint':
        """
        Filter detections by sequence ID.
        
        Args:
            sequence_id: Sequence identifier
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        if not sequence_id:
            raise ValueError("Sequence ID cannot be empty")
        
        self._filters["sequence_id"] = sequence_id
        return self
    
    def by_organization(self, organization_id: str) -> 'DetectionEndpoint':
        """
        Filter detections by organization ID.
        
        Args:
            organization_id: Organization identifier
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        if not organization_id:
            raise ValueError("Organization ID cannot be empty")
        
        self._filters["organization_id"] = organization_id
        return self
    
    def by_creator(self, creator_id: str) -> 'DetectionEndpoint':
        """
        Filter detections by creator ID.
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        if not creator_id:
            raise ValueError("Creator ID cannot be empty")
        
        self._filters["creator_id"] = creator_id
        return self
    
    def object_type(self, obj_type: str) -> 'DetectionEndpoint':
        """
        Filter detections by object type.
        
        Args:
            obj_type: Object type (e.g., 'traffic_sign', 'person', 'vehicle')
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        if not obj_type:
            raise ValueError("Object type cannot be empty")
        
        self._filters["object_type"] = obj_type
        return self
    
    def object_value(self, obj_value: str) -> 'DetectionEndpoint':
        """
        Filter detections by object value.
        
        Args:
            obj_value: Specific object value (e.g., 'stop', 'speed_limit_30')
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        if not obj_value:
            raise ValueError("Object value cannot be empty")
        
        self._filters["object_value"] = obj_value
        return self
    
    def min_confidence(self, confidence: float) -> 'DetectionEndpoint':
        """
        Filter detections by minimum confidence score.
        
        Args:
            confidence: Minimum confidence (0.0 to 1.0)
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        self._filters["min_confidence"] = confidence
        return self
    
    def traffic_signs(self) -> 'DetectionEndpoint':
        """
        Filter only traffic sign detections.
        
        Returns:
            DetectionEndpoint instance for method chaining
        """
        return self.object_type("traffic_sign")
    
    def traffic_lights(self) -> 'DetectionEndpoint':
        """
        Filter only traffic light detections.
        
        Returns:
            DetectionEndpoint instance for method chaining
        """
        return self.object_type("traffic_light")
    
    def persons(self) -> 'DetectionEndpoint':
        """
        Filter only person detections.
        
        Returns:
            DetectionEndpoint instance for method chaining
        """
        return self.object_type("person")
    
    def vehicles(self) -> 'DetectionEndpoint':
        """
        Filter only vehicle detections.
        
        Returns:
            DetectionEndpoint instance for method chaining
        """
        return self.object_type("vehicle")
    
    def created_between(
        self, 
        start_date: str, 
        end_date: Optional[str] = None
    ) -> 'DetectionEndpoint':
        """
        Filter detections by creation date range.
        
        Args:
            start_date: Start date
            end_date: End date (optional)
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        validate_date_string(start_date)
        self._filters["min_created_at"] = start_date
        
        if end_date:
            validate_date_string(end_date)
            self._filters["max_created_at"] = end_date
        
        return self
    
    def first_seen_between(
        self, 
        start_date: str, 
        end_date: Optional[str] = None
    ) -> 'DetectionEndpoint':
        """
        Filter detections by first seen date range.
        
        Args:
            start_date: Start date
            end_date: End date (optional)
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        validate_date_string(start_date)
        self._filters["min_first_seen_at"] = start_date
        
        if end_date:
            validate_date_string(end_date)
            self._filters["max_first_seen_at"] = end_date
        
        return self
    
    def last_seen_between(
        self, 
        start_date: str, 
        end_date: Optional[str] = None
    ) -> 'DetectionEndpoint':
        """
        Filter detections by last seen date range.
        
        Args:
            start_date: Start date
            end_date: End date (optional)
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        validate_date_string(start_date)
        self._filters["min_last_seen_at"] = start_date
        
        if end_date:
            validate_date_string(end_date)
            self._filters["max_last_seen_at"] = end_date
        
        return self
    
    def fields(self, *field_names: str) -> 'DetectionEndpoint':
        """
        Specify which fields to include in the response.
        
        Args:
            *field_names: Field names to include
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        if "all" in field_names:
            self._fields = ["all"]
        else:
            self._fields = list(field_names)
        
        return self
    
    def limit(self, count: int) -> 'DetectionEndpoint':
        """
        Limit the number of results.
        
        Args:
            count: Maximum number of results
            
        Returns:
            DetectionEndpoint instance for method chaining
        """
        if count <= 0:
            raise ValueError("Limit must be positive")
        
        self._filters["limit"] = count
        return self
    
    def get(self) -> APIResponse:
        """
        Execute the query and return results.
        
        Returns:
            APIResponse containing Detection objects
        """
        endpoint = "/map_features"  # Detections are part of map features
        params = self._build_params()
        
        response_data = self.client.get(endpoint, params=params)
        return APIResponse.from_dict(response_data, Detection)
    
    def get_by_id(self, detection_id: str, fields: Optional[List[str]] = None) -> Detection:
        """
        Get a specific detection by ID.
        
        Args:
            detection_id: Detection identifier
            fields: Fields to include in response
            
        Returns:
            Detection object
        """
        if not detection_id:
            raise ValueError("Detection ID cannot be empty")
        
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        elif self._fields:
            params["fields"] = ",".join(self._fields)
        
        response_data = self.client.get(f"/{detection_id}", params=params)
        return Detection.from_dict(response_data)
    
    def get_statistics(
        self, 
        group_by: str = "object_type"
    ) -> Dict[str, Any]:
        """
        Get statistics about detections.
        
        Args:
            group_by: Field to group statistics by
            
        Returns:
            Statistics dictionary
        """
        params = self._build_params()
        params["group_by"] = group_by
        params["statistics"] = True
        
        return self.client.get("/map_features/statistics", params=params)
    
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