from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.dashboard import DashboardStats
from app.services.user_service import UserService
from app.api.dependencies import get_current_user
from app.core.database import get_database

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
    user_service = UserService(db)
    return await user_service.update_user(current_user, update_data)

@router.get("/dashboard", response_model=DashboardStats)
async def get_user_dashboard(
    current_user: str = Depends(get_current_user),
    db = Depends(get_database)
):
    user_service = UserService(db)
    return await user_service.get_dashboard(current_user)