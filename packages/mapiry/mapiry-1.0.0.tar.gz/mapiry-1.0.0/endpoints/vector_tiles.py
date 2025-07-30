"""
Vector tile-related API endpoints for Mapiry SDK
"""

from typing import Optional, Dict, Any, List, Union
import json


class VectorTileEndpoint:
    """
    Handles vector tile-related API operations.
    
    This class provides methods to retrieve vector tiles for efficient
    map rendering and visualization.
    """
    
    def __init__(self, client):
        """
        Initialize the VectorTileEndpoint.
        
        Args:
            client: MapillaryClient instance
        """
        self.client = client
        self._layer = None
        self._z = None
        self._x = None
        self._y = None
    
    def get_tile(
        self, 
        layer: str, 
        z: int, 
        x: int, 
        y: int,
        format: str = "mvt"
    ) -> bytes:
        """
        Get a vector tile for the specified coordinates.
        
        Args:
            layer: Tile layer name ('image', 'sequence', 'overview', 'traffic_sign')
            z: Zoom level (0-14)
            x: Tile X coordinate
            y: Tile Y coordinate
            format: Tile format ('mvt' for Mapbox Vector Tiles)
            
        Returns:
            Vector tile data as bytes
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if layer not in ["image", "sequence", "overview", "traffic_sign", "map_feature"]:
            raise ValueError(f"Invalid layer: {layer}")
        
        if not 0 <= z <= 14:
            raise ValueError("Zoom level must be between 0 and 14")
        
        if not 0 <= x < (2 ** z):
            raise ValueError(f"X coordinate must be between 0 and {2**z - 1} for zoom level {z}")
        
        if not 0 <= y < (2 ** z):
            raise ValueError(f"Y coordinate must be between 0 and {2**z - 1} for zoom level {z}")
        
        # Build endpoint URL
        endpoint = f"/{layer}/{z}/{x}/{y}"
        if format != "mvt":
            endpoint += f".{format}"
        
        # Make request using vector tiles base URL
        response_data = self.client.request(
            method="GET",
            endpoint=endpoint,
            base_url=self.client.VECTOR_TILES_URL,
            use_oauth_header=False  # Vector tiles use access token as query parameter
        )
        
        return response_data.get("content", b"")
    
    def get_image_tiles(
        self, 
        z: int, 
        x: int, 
        y: int,
        format: str = "mvt"
    ) -> bytes:
        """
        Get image vector tiles.
        
        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            format: Tile format
            
        Returns:
            Vector tile data
        """
        return self.get_tile("image", z, x, y, format)
    
    def get_sequence_tiles(
        self, 
        z: int, 
        x: int, 
        y: int,
        format: str = "mvt"
    ) -> bytes:
        """
        Get sequence vector tiles.
        
        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            format: Tile format
            
        Returns:
            Vector tile data
        """
        return self.get_tile("sequence", z, x, y, format)
    
    def get_overview_tiles(
        self, 
        z: int, 
        x: int, 
        y: int,
        format: str = "mvt"
    ) -> bytes:
        """
        Get overview vector tiles.
        
        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            format: Tile format
            
        Returns:
            Vector tile data
        """
        return self.get_tile("overview", z, x, y, format)
    
    def get_traffic_sign_tiles(
        self, 
        z: int, 
        x: int, 
        y: int,
        format: str = "mvt"
    ) -> bytes:
        """
        Get traffic sign vector tiles.
        
        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            format: Tile format
            
        Returns:
            Vector tile data
        """
        return self.get_tile("traffic_sign", z, x, y, format)
    
    def get_coverage_tiles(
        self, 
        z: int, 
        x: int, 
        y: int,
        format: str = "mvt"
    ) -> bytes:
        """
        Get coverage vector tiles.
        
        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            format: Tile format
            
        Returns:
            Vector tile data
        """
        # Build endpoint URL
        endpoint = f"/{z}/{x}/{y}"
        if format != "mvt":
            endpoint += f".{format}"
        
        response_data = self.client.request(
            method="GET",
            endpoint=endpoint,
            base_url=self.client.COVERAGE_TILES_URL,
            use_oauth_header=False
        )
        
        return response_data.get("content", b"")
    
    def get_computed_coverage_tiles(
        self, 
        z: int, 
        x: int, 
        y: int,
        format: str = "mvt"
    ) -> bytes:
        """
        Get computed coverage vector tiles.
        
        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            format: Tile format
            
        Returns:
            Vector tile data
        """
        # Build endpoint URL
        endpoint = f"/{z}/{x}/{y}"
        if format != "mvt":
            endpoint += f".{format}"
        
        response_data = self.client.request(
            method="GET",
            endpoint=endpoint,
            base_url=self.client.COMPUTED_COVERAGE_TILES_URL,
            use_oauth_header=False
        )
        
        return response_data.get("content", b"")
    
    def get_map_feature_point_tiles(
        self, 
        z: int, 
        x: int, 
        y: int,
        format: str = "mvt"
    ) -> bytes:
        """
        Get map feature point vector tiles.
        
        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            format: Tile format
            
        Returns:
            Vector tile data
        """
        # Build endpoint URL
        endpoint = f"/{z}/{x}/{y}"
        if format != "mvt":
            endpoint += f".{format}"
        
        response_data = self.client.request(
            method="GET",
            endpoint=endpoint,
            base_url=self.client.MAP_FEATURES_POINTS_URL,
            use_oauth_header=False
        )
        
        return response_data.get("content", b"")
    
    def get_map_feature_traffic_sign_tiles(
        self, 
        z: int, 
        x: int, 
        y: int,
        format: str = "mvt"
    ) -> bytes:
        """
        Get map feature traffic sign vector tiles.
        
        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            format: Tile format
            
        Returns:
            Vector tile data
        """
        # Build endpoint URL
        endpoint = f"/{z}/{x}/{y}"
        if format != "mvt":
            endpoint += f".{format}"
        
        response_data = self.client.request(
            method="GET",
            endpoint=endpoint,
            base_url=self.client.MAP_FEATURES_TRAFFIC_SIGNS_URL,
            use_oauth_header=False
        )
        
        return response_data.get("content", b"")
    
    def get_tile_bounds(self, z: int, x: int, y: int) -> Dict[str, float]:
        """
        Get the geographic bounds of a tile.
        
        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            
        Returns:
            Dictionary with bounds (west, south, east, north)
        """
        import math
        
        # Calculate tile bounds
        n = 2.0 ** z
        lon_deg_west = x / n * 360.0 - 180.0
        lon_deg_east = (x + 1) / n * 360.0 - 180.0
        lat_rad_north = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat_rad_south = math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))
        lat_deg_north = math.degrees(lat_rad_north)
        lat_deg_south = math.degrees(lat_rad_south)
        
        return {
            "west": lon_deg_west,
            "south": lat_deg_south,
            "east": lon_deg_east,
            "north": lat_deg_north
        }
    
    def get_tiles_for_bbox(
        self, 
        west: float, 
        south: float, 
        east: float, 
        north: float,
        zoom: int
    ) -> List[Dict[str, int]]:
        """
        Get list of tile coordinates that cover a bounding box.
        
        Args:
            west: Western longitude boundary
            south: Southern latitude boundary
            east: Eastern longitude boundary
            north: Northern latitude boundary
            zoom: Zoom level
            
        Returns:
            List of tile coordinates
        """
        import math
        
        def _deg2num(lat_deg: float, lon_deg: float, zoom: int):
            lat_rad = math.radians(lat_deg)
            n = 2.0 ** zoom
            x_tile = int((lon_deg + 180.0) / 360.0 * n)
            y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
            return (x_tile, y_tile)
        
        # Calculate tile coordinates for the bounding box corners
        x_min, y_max = _deg2num(north, west, zoom)
        x_max, y_min = _deg2num(south, east, zoom)
        
        # Ensure proper ordering
        if x_min > x_max:
            x_min, x_max = x_max, x_min
        if y_min > y_max:
            y_min, y_max = y_max, y_min
        
        tiles = []
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                tiles.append({"x": x, "y": y, "z": zoom})
        
        return tiles
    
    def save_tile(
        self, 
        layer: str, 
        z: int, 
        x: int, 
        y: int,
        filename: str,
        format: str = "mvt"
    ) -> None:
        """
        Save a vector tile to file.
        
        Args:
            layer: Tile layer name
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            filename: Output filename
            format: Tile format
        """
        tile_data = self.get_tile(layer, z, x, y, format)
        
        with open(filename, "wb") as f:
            f.write(tile_data)
    
    def get_tile_metadata(self, layer: str) -> Dict[str, Any]:
        """
        Get metadata for a tile layer.
        
        Args:
            layer: Layer name
            
        Returns:
            Layer metadata
        """
        # This would typically come from a metadata endpoint
        # For now, return basic information
        layer_info = {
            "image": {
                "description": "Image points",
                "geometry_type": "Point",
                "fields": ["id", "captured_at", "compass_angle", "sequence_id"]
            },
            "sequence": {
                "description": "Image sequences",
                "geometry_type": "LineString", 
                "fields": ["id", "created_at", "captured_at", "creator_id"]
            },
            "overview": {
                "description": "Simplified overview data",
                "geometry_type": "Mixed",
                "fields": ["id", "type"]
            },
            "traffic_sign": {
                "description": "Traffic sign detections",
                "geometry_type": "Point",
                "fields": ["id", "object_type", "object_value", "confidence"]
            },
            "map_feature": {
                "description": "Map features and detections",
                "geometry_type": "Point",
                "fields": ["id", "feature_type", "feature_value", "confidence"]
            }
        }
        
        return layer_info.get(layer, {})