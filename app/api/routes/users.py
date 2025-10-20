from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, File
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.dashboard import DashboardStats
from app.services.user_service import UserService
from app.api.dependencies import get_current_user
from app.core.database import get_database
from app.services.storage_service import StorageService

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    user_service = UserService(db)
    return await user_service.get_user_by_username(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update user profile (username, display_name, etc.)"""
    user_service = UserService(db)
    return await user_service.update_user(current_user, update_data)


@router.put("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """Upload and update user avatar"""
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and GIF files are allowed"
        )
    
    # Upload to Cloudinary
    storage_service = StorageService()
    avatar_url = await storage_service.upload_avatar(file)
    
    # Update user document with new avatar URL
    user_service = UserService(db)
    return await user_service.update_avatar(current_user, avatar_url)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get current user profile"""
    user_service = UserService(db)
    return await user_service.get_user_by_username(current_user)

@router.get("/dashboard", response_model=DashboardStats)
async def get_user_dashboard(
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    user_service = UserService(db)
    return await user_service.get_dashboard(current_user)