from PIL import Image
import io
from typing import Tuple

def compress_image(image_bytes: bytes, max_size: Tuple[int, int] = (1920, 1080), quality: int = 85) -> bytes:
    """Compress and resize image"""
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert RGBA to RGB if necessary
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Resize if larger than max_size
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Compress
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    return output.read()

def validate_image(file_bytes: bytes) -> bool:
    """Validate if file is a valid image"""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
        return True
    except Exception:
        return False