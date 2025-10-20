import os
import io
import uuid
import cloudinary
import cloudinary.uploader
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.config import settings
from app.utils.image_processing import validate_image, compress_image
from typing import Optional


cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)

class StorageService:
    async def save_upload_file(
    upload_file: UploadFile,
    folder: Optional[str] = None  # Add folder parameter
    ) -> str:
        """Save uploaded file to Cloudinary and return URL"""
        
        # Validate file extension
        file_ext = upload_file.filename.split('.')[-1].lower()
        if file_ext not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed: {settings.allowed_extensions}"
            )
        
        # Read file
        file_bytes = await upload_file.read()

        return await StorageService.save_upload_file_bytes(
            file_bytes, 
            upload_file.filename,
            folder=folder  # Pass folder parameter
        )
    

    @staticmethod
    async def save_upload_file_bytes(
        file_bytes: bytes, 
        filename: str,
        folder: Optional[str] = None  # Add folder parameter
    ) -> str:
        """Save file bytes to Cloudinary and return URL"""
        
        # Validate file extension
        file_ext = filename.split('.')[-1].lower()
        if file_ext not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed: {settings.allowed_extensions}"
            )
        
        # Validate file size
        if len(file_bytes) > settings.max_file_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Max size: {settings.max_file_size} bytes"
            )
        
        # Validate image
        if not validate_image(file_bytes):
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Compress image
        compressed_bytes = compress_image(file_bytes)
        
        # Generate unique public_id
        unique_id = f"{uuid.uuid4()}"
        
        # Determine which folder to use
        upload_folder = folder if folder else settings.cloudinary_folder
        
        try:
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                io.BytesIO(compressed_bytes),
                folder=upload_folder,  # Use the determined folder
                public_id=unique_id,
                resource_type="image",
                format="jpg",
                transformation=[
                    {'width': 1920, 'height': 1080, 'crop': 'limit'},
                    {'quality': 'auto:good'}
                ]
            )
            
            # Return the secure URL
            return upload_result['secure_url']
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to upload image: {str(e)}"
            )
        
        # # Validate file size
        # if len(file_bytes) > settings.max_file_size:
        #     raise HTTPException(
        #         status_code=400, 
        #         detail=f"File too large. Max size: {settings.max_file_size} bytes"
        #     )
        
        # # Validate image
        # if not validate_image(file_bytes):
        #     raise HTTPException(status_code=400, detail="Invalid image file")
        
        # # Compress image
        # compressed_bytes = compress_image(file_bytes)
        
        # # Generate unique public_id
        # unique_id = f"{uuid.uuid4()}"
        
        # try:
        #     # Upload to Cloudinary
        #     upload_result = cloudinary.uploader.upload(
        #         io.BytesIO(compressed_bytes),
        #         folder=settings.cloudinary_folder,
        #         public_id=unique_id,
        #         resource_type="image",
        #         format="jpg",
        #         transformation=[
        #             {'width': 1920, 'height': 1080, 'crop': 'limit'},
        #             {'quality': 'auto:good'}
        #         ]
        #     )
            
        #     # Return the secure URL
        #     return upload_result['secure_url']
            
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=500, 
        #         detail=f"Failed to upload image: {str(e)}"
        #     )
    
    @staticmethod
    def delete_file(file_url: str):
        """Delete file from Cloudinary"""
        try:
            # Extract public_id from URL
            if 'cloudinary.com' in file_url:
                parts = file_url.split('/')
                public_id_with_ext = parts[-1]
                public_id = public_id_with_ext.rsplit('.', 1)[0]
                
                # Include folder in public_id
                full_public_id = f"{settings.cloudinary_folder}/{public_id}"
                
                # Delete from Cloudinary
                cloudinary.uploader.destroy(full_public_id, resource_type="image")
        except Exception as e:
            print(f"Failed to delete image from Cloudinary: {str(e)}")
            pass

    async def upload_avatar(self, file) -> str:
        """Upload avatar to Cloudinary and return the secure URL"""
        try:
            result = cloudinary.uploader.upload(
                file.file,
                folder="tankas_avatars",
                resource_type="auto",
                allowed_formats=["jpg", "jpeg", "png", "gif"],
                max_bytes=5242880,  # 5MB max
                transformation=[
                    {"width": 500, "height": 500, "crop": "fill"},
                    {"quality": "auto"}
                ]
            )
            return result["secure_url"]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File upload failed: {str(e)}"
            )

# class StorageService:
#     @staticmethod
#     async def save_upload_file(upload_file: UploadFile) -> str:
#         """Save uploaded file and return URL"""
#         # Validate file extension
#         file_ext = upload_file.filename.split('.')[-1].lower()
#         if file_ext not in settings.allowed_extensions:
#             raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {settings.allowed_extensions}")
        
#         # Read file
#         file_bytes = await upload_file.read()
        
#         # Validate file size
#         if len(file_bytes) > settings.max_file_size:
#             raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.max_file_size} bytes")
        
#         # Validate image
#         if not validate_image(file_bytes):
#             raise HTTPException(status_code=400, detail="Invalid image file")
        
#         # Compress image
#         compressed_bytes = compress_image(file_bytes)
        
#         # Generate unique filename
#         now = datetime.now()
#         year_month_dir = f"{now.year}/{now.month:02d}"
#         unique_filename = f"{uuid.uuid4()}.jpg"
        
#         # Create directory structure
#         upload_path = Path(settings.upload_dir) / year_month_dir
#         upload_path.mkdir(parents=True, exist_ok=True)
        
#         # Save file
#         file_path = upload_path / unique_filename
#         with open(file_path, 'wb') as f:
#             f.write(compressed_bytes)
        
#         # Return URL path
#         return f"/{settings.upload_dir}/{year_month_dir}/{unique_filename}"
    
#     @staticmethod
#     def delete_file(file_url: str):
#         """Delete file from storage"""
#         try:
#             file_path = file_url.lstrip('/')
#             if os.path.exists(file_path):
#                 os.remove(file_path)
#         except Exception:
#             pass  # Silently fail if file doesn't exist