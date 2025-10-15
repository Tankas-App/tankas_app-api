from PIL import Image
import piexif
from typing import Optional, Tuple
import io

def convert_to_degrees(value):
    """
    Helper function to convert GPS coordinates stored in EXIF to degrees in float format
    
    Args:
        value: GPS coordinate in EXIF format (tuple of tuples)
        
    Returns:
        Coordinate in decimal degrees
    """
    d = float(value[0][0]) / float(value[0][1])  # Degrees
    m = float(value[1][0]) / float(value[1][1])  # Minutes
    s = float(value[2][0]) / float(value[2][1])  # Seconds
    
    return d + (m / 60.0) + (s / 3600.0)

def extract_gps_from_image(image_bytes: bytes) -> Optional[Tuple[float, float]]:
    """
    Extract GPS coordinates (latitude, longitude) from image EXIF data
    
    Args:
        image_bytes: Image file as bytes
        
    Returns:
        Tuple of (latitude, longitude) or None if no GPS data found
    """
    try:
        # Open image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Get EXIF data
        exif_dict = piexif.load(image.info.get('exif', b''))
        
        # Check if GPS data exists
        if piexif.GPSIFD.GPSLatitude not in exif_dict['GPS']:
            return None
        
        # Extract GPS data
        gps_latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
        gps_latitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
        gps_longitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
        gps_longitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
        
        # Convert to decimal degrees
        latitude = convert_to_degrees(gps_latitude)
        if gps_latitude_ref == 'S':
            latitude = -latitude
        
        longitude = convert_to_degrees(gps_longitude)
        if gps_longitude_ref == 'W':
            longitude = -longitude
        
        return (latitude, longitude)
        
    except Exception as e:
        print(f"Error extracting GPS from EXIF: {str(e)}")
        return None

def get_exif_info(image_bytes: bytes) -> dict:
    """
    Get various EXIF metadata from image
    
    Returns:
        Dictionary with EXIF information including GPS, datetime, camera info
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif_dict = piexif.load(image.info.get('exif', b''))
        
        info = {
            'has_gps': piexif.GPSIFD.GPSLatitude in exif_dict.get('GPS', {}),
            'datetime': None,
            'camera_make': None,
            'camera_model': None,
            'gps_coordinates': None
        }
        
        # Get datetime
        if piexif.ImageIFD.DateTime in exif_dict.get('0th', {}):
            info['datetime'] = exif_dict['0th'][piexif.ImageIFD.DateTime].decode('utf-8')
        
        # Get camera info
        if piexif.ImageIFD.Make in exif_dict.get('0th', {}):
            info['camera_make'] = exif_dict['0th'][piexif.ImageIFD.Make].decode('utf-8')
        
        if piexif.ImageIFD.Model in exif_dict.get('0th', {}):
            info['camera_model'] = exif_dict['0th'][piexif.ImageIFD.Model].decode('utf-8')
        
        # Get GPS
        gps_coords = extract_gps_from_image(image_bytes)
        if gps_coords:
            info['gps_coordinates'] = {
                'latitude': gps_coords[0],
                'longitude': gps_coords[1]
            }
        
        return info
        
    except Exception as e:
        print(f"Error reading EXIF data: {str(e)}")
        return {}