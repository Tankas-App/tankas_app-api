import os
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.config import settings
from app.utils.image_processing import validate_image, compress_image

class StorageService:
    @staticmethod
    async def save_upload_file(upload_file: UploadFile) -> str:
        """Save uploaded file and return URL"""
        # Validate file extension
        file_ext = upload_file.filename.split('.')[-1].lower()
        if file_ext not in settings.allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {settings.allowed_extensions}")
        
        # Read file
        file_bytes = await upload_file.read()
        
        # Validate file size
        if len(file_bytes) > settings.max_file_size:
            raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.max_file_size} bytes")
        
        # Validate image
        if not validate_image(file_bytes):
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Compress image
        compressed_bytes = compress_image(file_bytes)
        
        # Generate unique filename
        now = datetime.now()
        year_month_dir = f"{now.year}/{now.month:02d}"
        unique_filename = f"{uuid.uuid4()}.jpg"
        
        # Create directory structure
        upload_path = Path(settings.upload_dir) / year_month_dir
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_path / unique_filename
        with open(file_path, 'wb') as f:
            f.write(compressed_bytes)
        
        # Return URL path
        return f"/{settings.upload_dir}/{year_month_dir}/{unique_filename}"
    
    @staticmethod
    def delete_file(file_url: str):
        """Delete file from storage"""
        try:
            file_path = file_url.lstrip('/')
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass  # Silently fail if file doesn't exist