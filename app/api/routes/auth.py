from fastapi import APIRouter, Depends
from app.schemas.auth import SignupRequest, LoginRequest, Token
from app.services.auth_service import AuthService
from app.core.database import get_database

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", response_model=Token)
async def signup(signup_data: SignupRequest, db = Depends(get_database)):
    auth_service = AuthService(db)
    return await auth_service.signup(signup_data)

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db = Depends(get_database)):
    auth_service = AuthService(db)
    return await auth_service.login(login_data)