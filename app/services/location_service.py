from typing import Dict

class LocationService:
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """Validate GPS coordinates"""
        return -90 <= latitude <= 90 and -180 <= longitude <= 180
    
    @staticmethod
    def create_geojson(latitude: float, longitude: float) -> Dict:
        """Convert lat/lng to GeoJSON format for MongoDB"""
        return {
            "type": "Point",
            "coordinates": [longitude, latitude]  # MongoDB uses [lng, lat]
        }
    
    @staticmethod
    def extract_coordinates(geojson: Dict) -> tuple:
        """Extract lat/lng from GeoJSON"""
        lng, lat = geojson["coordinates"]
        return lat, lng