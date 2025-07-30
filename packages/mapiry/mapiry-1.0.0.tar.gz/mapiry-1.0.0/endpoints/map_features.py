"""
Map Feature-related API endpoints for Mapiry SDK
"""

from typing import Optional, Dict, Any, List, Union
from ..models import MapFeature, APIResponse
from ..utils import (
    validate_coordinates, validate_bbox, validate_date_string,
    build_query_params
)


class MapFeatureEndpoint:
    """
    Handles map feature-related API operations.
    
    This class provides methods to search, filter, and retrieve map features
    from the Mapillary API.
    """
    
    def __init__(self, client):
        """
        Initialize the MapFeatureEndpoint.
        
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
    ) -> 'MapFeatureEndpoint':
        """
        Filter map features close to a specific point.
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            radius: Search radius in meters (optional)
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        validate_coordinates(latitude, longitude)
        
        self._filters.update({
            "closeto": f"{longitude},{latitude}"
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
    ) -> 'MapFeatureEndpoint':
        """
        Filter map features within a bounding box.
        
        Args:
            west: Western longitude boundary
            south: Southern latitude boundary
            east: Eastern longitude boundary
            north: Northern latitude boundary
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        validate_bbox(west, south, east, north)
        
        self._filters.update({
            "bbox": f"{west},{south},{east},{north}"
        })
        
        return self
    
    def object_values(self, *values: str) -> 'MapFeatureEndpoint':
        """
        Filter map features by object values.
        
        Args:
            *values: Object values to filter by (e.g., 'object--bench', 'object--fire-hydrant')
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        if not values:
            raise ValueError("At least one object value must be provided")
        
        self._filters["object_values"] = ",".join(values)
        return self
    
    def object_types(self, *types: str) -> 'MapFeatureEndpoint':
        """
        Filter map features by object types.
        
        Args:
            *types: Object types to filter by
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        if not types:
            raise ValueError("At least one object type must be provided")
        
        self._filters["object_types"] = ",".join(types)
        return self
    
    def by_image(self, image_id: str) -> 'MapFeatureEndpoint':
        """
        Filter map features by image ID.
        
        Args:
            image_id: Image identifier
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        if not image_id:
            raise ValueError("Image ID cannot be empty")
        
        self._filters["image_id"] = image_id
        return self
    
    def first_seen_after(self, date: str) -> 'MapFeatureEndpoint':
        """
        Filter map features first seen after a specific date.
        
        Args:
            date: Date string
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        validate_date_string(date)
        self._filters["first_seen_after"] = date
        return self
    
    def first_seen_before(self, date: str) -> 'MapFeatureEndpoint':
        """
        Filter map features first seen before a specific date.
        
        Args:
            date: Date string
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        validate_date_string(date)
        self._filters["first_seen_before"] = date
        return self
    
    def last_seen_after(self, date: str) -> 'MapFeatureEndpoint':
        """
        Filter map features last seen after a specific date.
        
        Args:
            date: Date string
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        validate_date_string(date)
        self._filters["last_seen_after"] = date
        return self
    
    def last_seen_before(self, date: str) -> 'MapFeatureEndpoint':
        """
        Filter map features last seen before a specific date.
        
        Args:
            date: Date string
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        validate_date_string(date)
        self._filters["last_seen_before"] = date
        return self
    
    def min_confidence(self, confidence: float) -> 'MapFeatureEndpoint':
        """
        Filter map features by minimum confidence score.
        
        Args:
            confidence: Minimum confidence (0.0 to 1.0)
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        self._filters["min_confidence"] = confidence
        return self
    
    def max_confidence(self, confidence: float) -> 'MapFeatureEndpoint':
        """
        Filter map features by maximum confidence score.
        
        Args:
            confidence: Maximum confidence (0.0 to 1.0)
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        self._filters["max_confidence"] = confidence
        return self
    
    def benches(self) -> 'MapFeatureEndpoint':
        """
        Filter only bench map features.
        
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        return self.object_values("object--bench")
    
    def fire_hydrants(self) -> 'MapFeatureEndpoint':
        """
        Filter only fire hydrant map features.
        
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        return self.object_values("object--fire-hydrant")
    
    def trash_cans(self) -> 'MapFeatureEndpoint':
        """
        Filter only trash can map features.
        
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        return self.object_values("object--trash-can")
    
    def mailboxes(self) -> 'MapFeatureEndpoint':
        """
        Filter only mailbox map features.
        
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        return self.object_values("object--mailbox")
    
    def fields(self, *field_names: str) -> 'MapFeatureEndpoint':
        """
        Specify which fields to include in the response.
        
        Args:
            *field_names: Field names to include
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        if "all" in field_names:
            self._fields = ["all"]
        else:
            self._fields = list(field_names)
        
        return self
    
    def limit(self, count: int) -> 'MapFeatureEndpoint':
        """
        Limit the number of results.
        
        Args:
            count: Maximum number of results
            
        Returns:
            MapFeatureEndpoint instance for method chaining
        """
        if count <= 0:
            raise ValueError("Limit must be positive")
        
        self._filters["limit"] = count
        return self
    
    def get(self) -> APIResponse:
        """
        Execute the query and return results.
        
        Returns:
            APIResponse containing MapFeature objects
        """
        endpoint = "/map_features"
        params = self._build_params()
        
        response_data = self.client.get(endpoint, params=params)
        return APIResponse.from_dict(response_data, MapFeature)
    
    def get_by_id(self, feature_id: str, fields: Optional[List[str]] = None) -> MapFeature:
        """
        Get a specific map feature by ID.
        
        Args:
            feature_id: Map feature identifier
            fields: Fields to include in response
            
        Returns:
            MapFeature object
        """
        if not feature_id:
            raise ValueError("Feature ID cannot be empty")
        
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        elif self._fields:
            params["fields"] = ",".join(self._fields)
        
        response_data = self.client.get(f"/{feature_id}", params=params)
        return MapFeature.from_dict(response_data)
    
    def get_detections(
        self, 
        feature_id: str, 
        fields: Optional[List[str]] = None
    ) -> APIResponse:
        """
        Get detections for a specific map feature.
        
        Args:
            feature_id: Map feature identifier
            fields: Fields to include in response
            
        Returns:
            APIResponse containing Detection objects
        """
        if not feature_id:
            raise ValueError("Feature ID cannot be empty")
        
        from .detections import DetectionEndpoint
        from ..models import Detection
        
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        
        endpoint = f"/{feature_id}/detections"
        response_data = self.client.get(endpoint, params=params)
        return APIResponse.from_dict(response_data, Detection)
    
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