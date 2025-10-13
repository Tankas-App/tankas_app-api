from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # MongoDB
    mongodb_uri: str
    database_name: str

    # Security
    jwt_secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # File Upload
    upload_dir: str = "./uploads"
    max_file_size: int = 5242880
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "webp"]

    # Storage Provider (local or cloudinary)
    use_cloudinary: bool = True
    
    # Cloudinary Configuration
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    cloudinary_folder: str = "tankas_app"  # Folder name in Cloudinary

    # CORS
    allowed_origins: List[str] = [
    "http://localhost:3000",      # React (if you had React)
    "http://localhost:5173",      # Vite (if you had Vite)
    "http://localhost:8080",      # NiceGUI default port
    "http://127.0.0.1:8080"       # Alternative localhost notation
    ]

    class Config:
        env_file = ".env"

settings = Settings()