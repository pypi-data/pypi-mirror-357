"""
Image-related API endpoints for Mapiry SDK
"""

from typing import Optional, Dict, Any, List, Union, Tuple
from ..models import Image, APIResponse
from ..utils import (
    validate_coordinates, validate_bbox, validate_date_string,
    validate_image_type, validate_compass_angle, build_query_params
)


class ImageEndpoint:
    """
    Handles image-related API operations.
    
    This class provides methods to search, filter, and retrieve images
    from the Mapillary API.
    """
    
    def __init__(self, client):
        """
        Initialize the ImageEndpoint.
        
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
    ) -> 'ImageEndpoint':
        """
        Filter images close to a specific point.
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            radius: Search radius in meters (optional)
            
        Returns:
            ImageEndpoint instance for method chaining
            
        Raises:
            ValidationError: If coordinates are invalid
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
    ) -> 'ImageEndpoint':
        """
        Filter images within a bounding box.
        
        Args:
            west: Western longitude boundary
            south: Southern latitude boundary
            east: Eastern longitude boundary
            north: Northern latitude boundary
            
        Returns:
            ImageEndpoint instance for method chaining
            
        Raises:
            ValidationError: If bounding box is invalid
        """
        validate_bbox(west, south, east, north)
        
        self._filters.update({
            "bbox": f"{west},{south},{east},{north}"
        })
        
        return self
    
    def by_sequence(self, sequence_id: str) -> 'ImageEndpoint':
        """
        Filter images by sequence ID.
        
        Args:
            sequence_id: Sequence identifier
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if not sequence_id:
            raise ValueError("Sequence ID cannot be empty")
        
        self._filters["sequence_id"] = sequence_id
        return self
    
    def by_organization(self, organization_id: str) -> 'ImageEndpoint':
        """
        Filter images by organization ID.
        
        Args:
            organization_id: Organization identifier
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if not organization_id:
            raise ValueError("Organization ID cannot be empty")
        
        self._filters["organization_id"] = organization_id
        return self
    
    def by_creator_username(self, username: str) -> 'ImageEndpoint':
        """
        Filter images by creator username.
        
        Args:
            username: Creator username
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if not username:
            raise ValueError("Username cannot be empty")
        
        self._filters["usernames"] = username
        return self
    
    def by_usernames(self, *usernames: str) -> 'ImageEndpoint':
        """
        Filter images by multiple creator usernames.
        
        Args:
            *usernames: Creator usernames
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if not usernames:
            raise ValueError("At least one username must be provided")
        
        self._filters["usernames"] = ",".join(usernames)
        return self
    
    def by_userkeys(self, *userkeys: str) -> 'ImageEndpoint':
        """
        Filter images by user keys.
        
        Args:
            *userkeys: User keys
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if not userkeys:
            raise ValueError("At least one user key must be provided")
        
        self._filters["userkeys"] = ",".join(userkeys)
        return self
    
    def by_image_keys(self, *image_keys: str) -> 'ImageEndpoint':
        """
        Filter images by image keys.
        
        Args:
            *image_keys: Image keys
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if not image_keys:
            raise ValueError("At least one image key must be provided")
        
        self._filters["image_keys"] = ",".join(image_keys)
        return self
    
    def by_sequence_keys(self, *sequence_keys: str) -> 'ImageEndpoint':
        """
        Filter images by sequence keys.
        
        Args:
            *sequence_keys: Sequence keys
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if not sequence_keys:
            raise ValueError("At least one sequence key must be provided")
        
        self._filters["sequence_keys"] = ",".join(sequence_keys)
        return self
    
    def by_organization_keys(self, *org_keys: str) -> 'ImageEndpoint':
        """
        Filter images by organization keys.
        
        Args:
            *org_keys: Organization keys
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if not org_keys:
            raise ValueError("At least one organization key must be provided")
        
        self._filters["organization_keys"] = ",".join(org_keys)
        return self
    
    def lookat(self, longitude: float, latitude: float) -> 'ImageEndpoint':
        """
        Filter images taken in the direction of a specific location.
        
        Args:
            longitude: Target longitude
            latitude: Target latitude
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        validate_coordinates(latitude, longitude)
        self._filters["lookat"] = f"{longitude},{latitude}"
        return self
    
    def private_images(self, private: bool = True) -> 'ImageEndpoint':
        """
        Filter images by privacy status.
        
        Args:
            private: True for private images, False for public images
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        self._filters["private"] = "true" if private else "false"
        return self
    
    def public_images(self) -> 'ImageEndpoint':
        """
        Filter only public images.
        
        Returns:
            ImageEndpoint instance for method chaining
        """
        return self.private_images(False)
    
    def per_page(self, count: int) -> 'ImageEndpoint':
        """
        Set number of images per page (alternative to limit).
        
        Args:
            count: Number of images per page (max 1000)
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if count <= 0 or count > 1000:
            raise ValueError("Per page count must be between 1 and 1000")
        
        self._filters["per_page"] = count
        return self
    
    def start_time(self, timestamp: str) -> 'ImageEndpoint':
        """
        Filter images captured since a specific timestamp.
        
        Args:
            timestamp: ISO timestamp string
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        validate_date_string(timestamp)
        self._filters["start_time"] = timestamp
        return self
    
    def end_time(self, timestamp: str) -> 'ImageEndpoint':
        """
        Filter images captured before a specific timestamp.
        
        Args:
            timestamp: ISO timestamp string
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        validate_date_string(timestamp)
        self._filters["end_time"] = timestamp
        return self
    
    def captured_between(
        self, 
        start_date: str, 
        end_date: Optional[str] = None
    ) -> 'ImageEndpoint':
        """
        Filter images by capture date range.
        
        Args:
            start_date: Start date (YYYY, YYYY-MM, or YYYY-MM-DDTHH:MM:SS)
            end_date: End date (optional)
            
        Returns:
            ImageEndpoint instance for method chaining
            
        Raises:
            ValidationError: If date format is invalid
        """
        validate_date_string(start_date)
        self._filters["min_captured_at"] = start_date
        
        if end_date:
            validate_date_string(end_date)
            self._filters["max_captured_at"] = end_date
        
        return self
    
    def captured_after(self, date: str) -> 'ImageEndpoint':
        """
        Filter images captured after a specific date.
        
        Args:
            date: Date string (YYYY, YYYY-MM, or YYYY-MM-DDTHH:MM:SS)
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        return self.captured_between(date)
    
    def captured_before(self, date: str) -> 'ImageEndpoint':
        """
        Filter images captured before a specific date.
        
        Args:
            date: Date string (YYYY, YYYY-MM, or YYYY-MM-DDTHH:MM:SS)
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        validate_date_string(date)
        self._filters["max_captured_at"] = date
        return self
    
    def image_type(self, img_type: str) -> 'ImageEndpoint':
        """
        Filter images by type.
        
        Args:
            img_type: Image type ('flat', 'pano', 'both', 'all')
            
        Returns:
            ImageEndpoint instance for method chaining
            
        Raises:
            ValidationError: If image type is invalid
        """
        validate_image_type(img_type)
        self._filters["image_type"] = img_type
        return self
    
    def compass_angle(
        self, 
        angle: Union[float, Tuple[float, float]]
    ) -> 'ImageEndpoint':
        """
        Filter images by compass angle or angle range.
        
        Args:
            angle: Single angle or tuple of (min_angle, max_angle)
            
        Returns:
            ImageEndpoint instance for method chaining
            
        Raises:
            ValidationError: If angle is invalid
        """
        validate_compass_angle(angle)
        
        if isinstance(angle, (tuple, list)):
            self._filters["compass_angle"] = f"{angle[0]},{angle[1]}"
        else:
            self._filters["compass_angle"] = angle
        
        return self
    
    def camera_make(self, make: str) -> 'ImageEndpoint':
        """
        Filter images by camera make.
        
        Args:
            make: Camera manufacturer
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if not make:
            raise ValueError("Camera make cannot be empty")
        
        self._filters["camera_make"] = make
        return self
    
    def camera_model(self, model: str) -> 'ImageEndpoint':
        """
        Filter images by camera model.
        
        Args:
            model: Camera model
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if not model:
            raise ValueError("Camera model cannot be empty")
        
        self._filters["camera_model"] = model
        return self
    
    def panoramic_only(self) -> 'ImageEndpoint':
        """
        Filter only panoramic images.
        
        Returns:
            ImageEndpoint instance for method chaining
        """
        return self.image_type("pano")
    
    def flat_only(self) -> 'ImageEndpoint':
        """
        Filter only flat (non-panoramic) images.
        
        Returns:
            ImageEndpoint instance for method chaining
        """
        return self.image_type("flat")
    
    def fields(self, *field_names: str) -> 'ImageEndpoint':
        """
        Specify which fields to include in the response.
        
        Args:
            *field_names: Field names to include
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if "all" in field_names:
            self._fields = ["all"]
        else:
            self._fields = list(field_names)
        
        return self
    
    def limit(self, count: int) -> 'ImageEndpoint':
        """
        Limit the number of results.
        
        Args:
            count: Maximum number of results
            
        Returns:
            ImageEndpoint instance for method chaining
        """
        if count <= 0:
            raise ValueError("Limit must be positive")
        
        self._filters["limit"] = count
        return self
    
    def get(self) -> APIResponse:
        """
        Execute the query and return results.
        
        Returns:
            APIResponse containing Image objects
        """
        # Determine endpoint based on filters
        if "longitude" in self._filters and "latitude" in self._filters:
            endpoint = "/images"
            params = self._build_params()
        elif "bbox" in self._filters:
            endpoint = "/images"
            params = self._build_params()
        else:
            endpoint = "/images"
            params = self._build_params()
        
        # Make API request
        response_data = self.client.get(endpoint, params=params)
        
        # Parse response
        return APIResponse.from_dict(response_data, Image)
    
    def get_by_id(self, image_id: str, fields: Optional[List[str]] = None) -> Image:
        """
        Get a specific image by ID.
        
        Args:
            image_id: Image identifier
            fields: Fields to include in response
            
        Returns:
            Image object
        """
        if not image_id:
            raise ValueError("Image ID cannot be empty")
        
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        elif self._fields:
            params["fields"] = ",".join(self._fields)
        
        response_data = self.client.get(f"/{image_id}", params=params)
        return Image.from_dict(response_data)
    
    def download_image(
        self, 
        image_id: str, 
        size: str = "thumb_2048_url"
    ) -> bytes:
        """
        Download image data.
        
        Args:
            image_id: Image identifier
            size: Image size ('thumb_256_url', 'thumb_1024_url', 'thumb_2048_url', 'thumb_original_url')
            
        Returns:
            Image data as bytes
        """
        # First get the image metadata to get the download URL
        image = self.get_by_id(image_id, fields=[size])
        
        # Get the URL for the requested size
        url = getattr(image, size, None)
        if not url:
            raise ValueError(f"Image size '{size}' not available for image {image_id}")
        
        # Download the image
        response = self.client.session.get(url)
        response.raise_for_status()
        
        return response.content
    
    def get_detections(
        self, 
        image_id: str, 
        fields: Optional[List[str]] = None
    ) -> APIResponse:
        """
        Get detections for a specific image.
        
        Args:
            image_id: Image identifier
            fields: Fields to include in response
            
        Returns:
            APIResponse containing Detection objects
        """
        if not image_id:
            raise ValueError("Image ID cannot be empty")
        
        from .detections import DetectionEndpoint
        from ..models import Detection
        
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        
        endpoint = f"/{image_id}/detections"
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